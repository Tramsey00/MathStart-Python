"""Own a Windows process tree before its first instruction executes.

Uses documented Job Objects and Toolhelp thread APIs, without breakaway flags
or changes to an enclosing sandbox job. Refused ownership fails closed.
https://learn.microsoft.com/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject
https://learn.microsoft.com/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information
"""
import ctypes as c
from ctypes import wintypes as w
import time


class BasicLimits(c.Structure):
    _fields_ = [('process_time',c.c_longlong),('job_time',c.c_longlong),('flags',w.DWORD),
                ('min_working',c.c_size_t),('max_working',c.c_size_t),('active_limit',w.DWORD),
                ('affinity',c.c_size_t),('priority',w.DWORD),('scheduling',w.DWORD)]


class ExtendedLimits(c.Structure):
    _fields_ = [('basic',BasicLimits),('io',c.c_ulonglong * 6),
                ('process_memory',c.c_size_t),('job_memory',c.c_size_t),
                ('peak_process',c.c_size_t),('peak_job',c.c_size_t)]


class Accounting(c.Structure):
    _fields_ = [('user',c.c_longlong),('kernel',c.c_longlong),
                ('period_user',c.c_longlong),('period_kernel',c.c_longlong),
                ('faults',w.DWORD),('total',w.DWORD),('active',w.DWORD),('terminated',w.DWORD)]


class ThreadEntry(c.Structure):
    _fields_ = [('size',w.DWORD),('usage',w.DWORD),('thread_id',w.DWORD),
                ('process_id',w.DWORD),('base_priority',w.LONG),('delta_priority',w.LONG),('flags',w.DWORD)]


class WindowsJob:
    def __init__(self):
        self.api = c.WinDLL('kernel32',use_last_error=True)
        declarations = {
            'CreateJobObjectW':([c.c_void_p,w.LPCWSTR],w.HANDLE),
            'SetInformationJobObject':([w.HANDLE,c.c_int,c.c_void_p,w.DWORD],w.BOOL),
            'AssignProcessToJobObject':([w.HANDLE,w.HANDLE],w.BOOL),
            'TerminateJobObject':([w.HANDLE,w.UINT],w.BOOL),
            'QueryInformationJobObject':([w.HANDLE,c.c_int,c.c_void_p,w.DWORD,c.c_void_p],w.BOOL),
            'OpenProcess':([w.DWORD,w.BOOL,w.DWORD],w.HANDLE),
            'CloseHandle':([w.HANDLE],w.BOOL),
            'CreateToolhelp32Snapshot':([w.DWORD,w.DWORD],w.HANDLE),
            'Thread32First':([w.HANDLE,c.POINTER(ThreadEntry)],w.BOOL),
            'Thread32Next':([w.HANDLE,c.POINTER(ThreadEntry)],w.BOOL),
            'OpenThread':([w.DWORD,w.BOOL,w.DWORD],w.HANDLE),
            'ResumeThread':([w.HANDLE],w.DWORD),
        }
        for name,(arguments,result) in declarations.items():
            method = getattr(self.api,name)
            method.argtypes,method.restype = arguments,result
        self.handle = self.api.CreateJobObjectW(None,None)
        if not self.handle:
            raise OSError('Cannot create owned process job')
        limits = ExtendedLimits()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.api.SetInformationJobObject(self.handle,9,c.byref(limits),c.sizeof(limits)):
            self.api.CloseHandle(self.handle)
            self.handle = None
            raise OSError('Cannot configure owned process job')

    def assign_and_resume(self,pid):
        process = self.api.OpenProcess(0x0100 | 0x0001,False,pid)  # SET_QUOTA | TERMINATE
        if not process:
            raise OSError('Cannot open owned suspended process')
        try:
            if not self.api.AssignProcessToJobObject(self.handle,process):
                raise OSError('Cannot assign owned process job')
        finally:
            self.api.CloseHandle(process)
        snapshot = self.api.CreateToolhelp32Snapshot(0x00000004,0)  # SNAPTHREAD
        if snapshot in (None,c.c_void_p(-1).value):
            raise OSError('Cannot inspect owned suspended thread')
        try:
            entry = ThreadEntry()
            entry.size = c.sizeof(entry)
            present = self.api.Thread32First(snapshot,c.byref(entry))
            while present:
                if entry.process_id == pid:
                    thread = self.api.OpenThread(0x0002,False,entry.thread_id)  # SUSPEND_RESUME
                    if not thread:
                        raise OSError('Cannot open owned suspended thread')
                    try:
                        if self.api.ResumeThread(thread) != 1:
                            raise OSError('Owned thread was not resumed exactly once')
                    finally:
                        self.api.CloseHandle(thread)
                    return
                present = self.api.Thread32Next(snapshot,c.byref(entry))
            raise OSError('Owned suspended thread was not found')
        finally:
            self.api.CloseHandle(snapshot)

    def stop(self):
        if not self.handle:
            return
        try:
            if not self.api.TerminateJobObject(self.handle,1):
                raise OSError('Owned job termination refused')
            deadline = time.monotonic() + 5
            while True:
                accounting = Accounting()
                if not self.api.QueryInformationJobObject(self.handle,1,c.byref(accounting),c.sizeof(accounting),None):
                    raise OSError('Cannot verify owned job termination')
                if accounting.active == 0:
                    return
                if time.monotonic() >= deadline:
                    raise OSError('Owned job descendants survived termination')
                time.sleep(0.05)
        finally:
            # Kill-on-close is also the last line of cleanup after API failure.
            self.api.CloseHandle(self.handle)
            self.handle = None
