import {StrictMode} from 'react';
import {it,expect,vi,beforeEach} from 'vitest';
import {render,screen,fireEvent,act} from '@testing-library/react';
const call=vi.hoisted(()=>vi.fn());
vi.mock('../src/shared/api/client',()=>({createApiClient:()=>({call})}));
import {SessionProvider,useSession} from '../src/features/identity/session';
function Consumer(){const {user,status,refresh}=useSession();return <><output>{status}:{user?.username??'anonymous'}</output><button onClick={()=>void refresh()}>After mutation</button></>;}
beforeEach(()=>{call.mockReset();});
it('shares simultaneous automatic reads without losing the StrictMode readiness result',async()=>{
 let finish!:(r:any)=>void;call.mockImplementation(()=>new Promise(resolve=>{finish=resolve;}));
 render(<StrictMode><SessionProvider><Consumer/></SessionProvider></StrictMode>);
 fireEvent.focus(window);fireEvent.focus(window);expect(call).toHaveBeenCalledTimes(1);
 finish({ok:true,value:{data:{id:1,username:'same-session'}}});await screen.findByText('ready:same-session');
});
it('uses a fresh post-mutation read and never restores the preceding session from an older response',async()=>{
 const finish:Array<(r:any)=>void>=[];call.mockImplementation(()=>new Promise(resolve=>finish.push(resolve)));
 render(<SessionProvider><Consumer/></SessionProvider>);
 fireEvent.click(screen.getByRole('button',{name:'After mutation'}));fireEvent.focus(window);expect(call).toHaveBeenCalledTimes(2);
 await act(async()=>{finish[0]!({ok:true,value:{data:{id:1,username:'previous-session'}}});});
 expect(screen.queryByText('ready:previous-session')).toBeNull();
 finish[1]!({ok:true,value:{data:{id:2,username:'new-session'}}});await screen.findByText('ready:new-session');
 expect(screen.queryByText('ready:previous-session')).toBeNull();
});
