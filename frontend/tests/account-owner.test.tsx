import {afterEach,describe,it,expect,vi} from 'vitest';
import {render,screen,cleanup,act} from '@testing-library/react';
import {MemoryRouter} from 'react-router';
const mocks=vi.hoisted(()=>({call:vi.fn(),user:{id:'owner-a',username:'synthetic-a',selected_grade_id:null},refresh:vi.fn()}));
vi.mock('../src/features/identity/session',()=>({api:{call:mocks.call},useSession:()=>({user:mocks.user,status:'ready',refresh:mocks.refresh}),safeReturn:()=>'/account/'}));
vi.mock('../src/features/public-pages/orbit-shell',()=>({OrbitShell:({children}:{children:React.ReactNode})=>children}));
import {AccountPage} from '../src/features/identity/account-page';
function view(){return <MemoryRouter initialEntries={['/account/?section=account']}><AccountPage/></MemoryRouter>;}
const state=(email:string)=>({ok:true,value:{data:{email,email_verified:true,mail_available:false}}});
afterEach(()=>{cleanup();vi.clearAllMocks();mocks.user={id:'owner-a',username:'synthetic-a',selected_grade_id:null};});
describe('MS-T009 account read ownership',()=>{
 it('hides the previous owner email immediately when the session owner changes',async()=>{
  mocks.call.mockImplementation((operation:string)=>operation==='list_grades'?Promise.resolve({ok:true,value:{data:[],meta:{}}}):mocks.user.id==='owner-a'?Promise.resolve(state('a@example.test')):new Promise(()=>{}));
  const result=render(view());await screen.findByText('a@example.test');
  mocks.user={id:'owner-b',username:'synthetic-b',selected_grade_id:null};result.rerender(view());
  expect(screen.queryByText('a@example.test')).toBeNull();
 });
 it('ignores an old owner response arriving after the new owner response',async()=>{
  let finishOld:(value:ReturnType<typeof state>)=>void=()=>{};
  mocks.call.mockImplementation((operation:string)=>operation==='list_grades'?Promise.resolve({ok:true,value:{data:[],meta:{}}}):mocks.user.id==='owner-a'?new Promise(resolve=>{finishOld=resolve;}):Promise.resolve(state('b@example.test')));
  const result=render(view());mocks.user={id:'owner-b',username:'synthetic-b',selected_grade_id:null};result.rerender(view());
  await screen.findByText('b@example.test');await act(async()=>{finishOld(state('a@example.test'));});
  expect(screen.queryByText('a@example.test')).toBeNull();expect(screen.getByText('b@example.test')).toBeTruthy();
 });
});
