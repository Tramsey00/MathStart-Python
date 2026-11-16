import {afterEach,it,expect,vi} from 'vitest';
import {render} from '@testing-library/react';
import {MemoryRouter} from 'react-router';
import type {ReactNode} from 'react';
const state=vi.hoisted(()=>({user:null as null|{id:number},replace:vi.fn()}));
vi.mock('../src/features/identity/session',async original=>({...await original<object>(),useSession:()=>({user:state.user,status:'ready',refresh:vi.fn()})}));
vi.mock('../src/shared/ui/use-site-theme',()=>({useSiteTheme:()=>[false,vi.fn()]}));
vi.mock('../src/features/identity/auth-mode-transition',()=>({AuthModeTransition:({children}:{children:ReactNode})=>children}));
import {AuthPage} from '../src/features/identity/account-page';
afterEach(()=>{vi.unstubAllGlobals();state.user=null;state.replace.mockClear();});
it.each([
 ['/auth?mode=login&return=%2Fadmin%2Fauth%2Fuser%2F','/admin/auth/user/'],
 ['/auth?mode=login&return=https%3A%2F%2Fexample.test','/account/'],
 ['/auth?mode=register&return=%2Fadmin%2F','/account/'],
])('honors only a safe login return after the session becomes authenticated: %s',(entry,expected)=>{
 vi.stubGlobal('location',{hash:'',pathname:'/auth',search:entry.slice(entry.indexOf('?')),replace:state.replace});
 const view=()=> <MemoryRouter initialEntries={[entry]}><AuthPage/></MemoryRouter>;
 const result=render(view());expect(state.replace).not.toHaveBeenCalled();
 state.user={id:4};result.rerender(view());
 expect(state.replace).toHaveBeenLastCalledWith(expected);
});
