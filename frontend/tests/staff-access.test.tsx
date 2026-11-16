import {it,expect,vi,beforeEach} from 'vitest';
import {render,screen,waitFor,fireEvent} from '@testing-library/react';
const state=vi.hoisted(()=>({user:{id:1},status:'ready',pathname:'/admin/',own:true,read:true,call:vi.fn(),load:vi.fn()}));
vi.mock('react-router',()=>({useLocation:()=>({pathname:state.pathname}),useNavigate:()=>vi.fn(),Link:({to,...props}:any)=><a href={to} {...props}/>}));
vi.mock('../src/features/identity/session',()=>({useSession:()=>({user:state.user,status:state.status,refresh:async()=>state.user}),safeReturn:(p:string)=>p,api:{call:state.call}}));
vi.mock('../src/shared/api/staff-capabilities',async original=>({...await original<object>(),loadStaffCapabilities:state.load}));
vi.mock('../src/shared/lesson/lesson-shell',()=>({LessonHeader:()=>null,LessonFooter:()=>null}));
vi.mock('../src/shared/ui/use-site-theme',()=>({useSiteTheme:()=>[false,vi.fn()]}));
import {StaffWorkspace} from '../src/shared/ui/staff-workspace';
const hints=()=>({version:1,own_password:state.own,resources:Object.fromEntries(['grades','subjects','sections','pages','publications','media_assets','redirects','users','groups'].map(n=>[n,{view:state.read,add:false,change:false,delete:false}]))});
beforeEach(()=>{state.user={id:1};state.status='ready';state.pathname='/admin/';state.own=true;state.read=true;state.call.mockReset().mockImplementation(async()=>({ok:true,value:{data:state.user}}));state.load.mockReset().mockImplementation(async()=>hints());});
it('never mounts staff sidebar or private children for authenticated non-staff',async()=>{
 state.own=false;state.read=false;const privateRender=vi.fn(()=> <input aria-label="private"/>);
 function Private(){return privateRender();}
 render(<StaffWorkspace><Private/></StaffWorkspace>);
 expect(screen.queryByLabelText('private')).toBeNull();
 await screen.findByRole('heading',{name:'Нет доступа'});
 expect(screen.queryByRole('navigation',{name:'Администрирование'})).toBeNull();expect(privateRender).not.toHaveBeenCalled();
});
it('blocks a direct form URL when staff has only view permission',async()=>{
 state.pathname='/admin/auth/user/add/';render(<StaffWorkspace><input aria-label="private form"/></StaffWorkspace>);
 await screen.findByRole('heading',{name:'Нет доступа'});expect(screen.queryByLabelText('private form')).toBeNull();
 expect(screen.getByRole('navigation',{name:'Администрирование'})).toBeTruthy();
});
it('keeps ordinary edits and the mounted form across blur and successful focus revalidation',async()=>{
 render(<StaffWorkspace><input aria-label="draft" defaultValue=""/></StaffWorkspace>);
 const input=await screen.findByLabelText('draft');fireEvent.change(input,{target:{value:'ordinary unsaved edit'}});
 fireEvent.blur(window);fireEvent.focus(window);
 await waitFor(()=>expect(screen.queryByRole('heading',{name:'Проверяем доступ'})).toBeNull());
 expect(screen.getByLabelText('draft')).toBe(input);expect((input as HTMLInputElement).value).toBe('ordinary unsaved edit');
});
it('unmounts old private data and removes navigation when staff is revoked',async()=>{
 render(<StaffWorkspace><input aria-label="private"/></StaffWorkspace>);await screen.findByLabelText('private');
 state.own=false;state.read=false;fireEvent.focus(window);
 await screen.findByRole('heading',{name:'Нет доступа'});expect(screen.queryByLabelText('private')).toBeNull();expect(screen.queryByRole('navigation',{name:'Администрирование'})).toBeNull();
});
it('replaces the private form after an account changes on return',async()=>{
 render(<StaffWorkspace><input aria-label="draft"/></StaffWorkspace>);const old=await screen.findByLabelText('draft');fireEvent.change(old,{target:{value:'previous actor'}});
 state.user={id:2};fireEvent.focus(window);
 await waitFor(()=>expect((screen.getByLabelText('draft') as HTMLInputElement).value).toBe(''));
 expect(screen.getByLabelText('draft')).not.toBe(old);
});

it('waits for shared session readiness before starting its own fresh authorization check',async()=>{
 state.status='checking';const view=()=> <StaffWorkspace><input aria-label="private"/></StaffWorkspace>;
 const result=render(view());expect(state.call).not.toHaveBeenCalled();expect(state.load).not.toHaveBeenCalled();expect(screen.queryByLabelText('private')).toBeNull();
 state.status='ready';result.rerender(view());await screen.findByLabelText('private');
 expect(state.call).toHaveBeenCalledTimes(1);expect(state.load).toHaveBeenCalledTimes(1);
});

it('coalesces overlapping return events while keeping both actor checks around fresh capabilities',async()=>{
 render(<StaffWorkspace><input aria-label="private"/></StaffWorkspace>);await screen.findByLabelText('private');
 let finish!:(value:any)=>void;state.call.mockClear();state.load.mockClear();state.call.mockImplementationOnce(()=>new Promise(resolve=>{finish=resolve;}));
 fireEvent.focus(window);fireEvent.focus(window);fireEvent(window,new Event('mathstart-staff-denied'));
 expect(state.call).toHaveBeenCalledTimes(1);expect(state.load).not.toHaveBeenCalled();
 finish({ok:true,value:{data:state.user}});
 await waitFor(()=>expect(screen.queryByRole('heading',{name:'Проверяем доступ'})).toBeNull());
 expect(state.call).toHaveBeenCalledTimes(2);expect(state.load).toHaveBeenCalledTimes(1);
});

it('does not mount the next route until that path has passed a fresh gate',async()=>{
 const view=(label:string)=> <StaffWorkspace><input aria-label={label}/></StaffWorkspace>;
 const result=render(view('old page'));await screen.findByLabelText('old page');
 let finish!:(value:any)=>void;state.call.mockImplementationOnce(()=>new Promise(resolve=>{finish=resolve;}));state.pathname='/admin/auth/user/';result.rerender(view('new page'));
 expect(screen.queryByLabelText('old page')).toBeNull();expect(screen.queryByLabelText('new page')).toBeNull();
 finish({ok:true,value:{data:state.user}});await screen.findByLabelText('new page');
});

it('locks a draft on transport failure and restores the same form only after a fresh successful check',async()=>{
 render(<StaffWorkspace><input aria-label="draft"/></StaffWorkspace>);const input=await screen.findByLabelText('draft');fireEvent.change(input,{target:{value:'unsaved edit'}});
 state.call.mockResolvedValue({ok:false,error:{code:'NETWORK_ERROR'}});fireEvent.focus(window);
 await screen.findByRole('heading',{name:'Не удалось проверить доступ'});
 expect(input.closest('.staff-frame')?.hasAttribute('hidden')).toBe(true);expect(input.closest('.staff-frame')?.hasAttribute('inert')).toBe(true);
 state.call.mockImplementation(async()=>({ok:true,value:{data:state.user}}));fireEvent.click(screen.getByRole('button',{name:'Повторить проверку'}));
 await waitFor(()=>expect(screen.queryByRole('heading',{name:'Проверяем доступ'})).toBeNull());
 expect(screen.getByLabelText('draft')).toBe(input);expect((input as HTMLInputElement).value).toBe('unsaved edit');expect(input.closest('.staff-frame')?.hasAttribute('hidden')).toBe(false);
});
