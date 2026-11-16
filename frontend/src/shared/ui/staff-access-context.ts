import {createContext,useContext} from 'react';
import {emptyStaffCapabilities,type StaffCapabilities} from '../api/staff-capabilities';

// Keep provider identity stable when the workspace presentation changes via HMR.
export const StaffAccess=createContext<StaffCapabilities>(emptyStaffCapabilities());
export const useStaffCapabilities=()=>useContext(StaffAccess);
