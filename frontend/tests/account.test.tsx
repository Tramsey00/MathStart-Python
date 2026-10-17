import {beforeEach,it,expect,vi} from 'vitest';
import {act,fireEvent,render,screen,waitFor} from '@testing-library/react';
const {call}=vi.hoisted(()=>({call:vi.fn()}));
vi.mock('../src/shared/api/client',()=>({createApiClient:()=>({call})}));
import AccountPage from '../src/app/routes/account-foundation';

const anonymous={ok:false,error:{code:'AUTHENTICATION_REQUIRED',message:'Войдите в аккаунт.',outcome:'rejected'}};
const unavailable={ok:false,error:{code:'SERVICE_UNAVAILABLE',message:'Сервис временно недоступен.',outcome:'unknown'}};
const user=(username:string,id=1)=>({ok:true,value:{data:{id,username,selected_grade_id:null,onboarding_mode:null,onboarding_complete:false}}});
const grades={ok:true,value:{data:[{id:73,title:'5 класс'}],meta:{pagination:{next_cursor:null}}}};
beforeEach(()=>{call.mockReset();call.mockImplementation(async op=>op==='list_grades'?grades:anonymous);});

it('keeps anonymous state quiet and distinguishes old login names from registration limit',async()=>{
 render(<AccountPage/>);await screen.findByLabelText('Пароль');
 expect(screen.getByRole('status').textContent).toBe('');
 expect(screen.getByLabelText('Имя пользователя').getAttribute('maxlength')).toBe('150');
 fireEvent.click(screen.getByRole('button',{name:'Регистрация',exact:true}));
 expect(screen.getByLabelText('Имя пользователя').getAttribute('maxlength')).toBe('30');
});

it('ignores an earlier GET response after a newer reconciliation completes',async()=>{
 let finish!:(r:unknown)=>void;
 call.mockImplementation(op=>op==='list_grades'?Promise.resolve(grades):Promise.resolve(user('Current owner',2)));
 call.mockImplementationOnce(()=>new Promise(resolve=>{finish=resolve;}));
 render(<AccountPage/>);
 fireEvent.click(screen.getByRole('button',{name:'Загрузить сохранённое состояние'}));
 await screen.findByText('Current owner');
 await act(async()=>finish(user('Stale owner',1)));
 expect(screen.queryByText('Stale owner')).toBeNull();
 expect(screen.getByText('Current owner')).toBeTruthy();
});

async function enter(mode:'login'|'register'){
 await screen.findByLabelText('Пароль');
 if(mode==='register')fireEvent.click(screen.getByRole('button',{name:'Регистрация',exact:true}));
 fireEvent.change(screen.getByLabelText('Имя пользователя'),{target:{value:'syntheticStudent'}});
 fireEvent.change(screen.getByLabelText('Пароль'),{target:{value:'Qm9!Vx2#Lr7@Zh4%'}});
 fireEvent.submit(screen.getByLabelText('Пароль').closest('form')!);
}

it('clears password and reconciles unknown login without retrying unsafe POST',async()=>{
 call.mockImplementation(async op=>op==='list_grades'?grades:op==='login'?unavailable:anonymous);
 render(<AccountPage/>);await enter('login');
 await waitFor(()=>expect(screen.getByRole('status').textContent).toBe('Войдите или зарегистрируйтесь.'));
 expect((screen.getByLabelText('Пароль') as HTMLInputElement).value).toBe('');
 expect(call.mock.calls.filter(([op])=>op==='login')).toHaveLength(1);
 expect(screen.queryByRole('button',{name:'Повторить тот же запрос'})).toBeNull();
});

it('discards pending registration credentials after GET observes a different owner',async()=>{
 let registrations=0;
 call.mockImplementation(async op=>op==='list_grades'?grades:op==='register'?(registrations++,unavailable):registrations?user('Other owner',2):anonymous);
 render(<AccountPage/>);await enter('register');
 await screen.findByText('Other owner');
 expect(screen.queryByRole('button',{name:'Повторить тот же запрос'})).toBeNull();
 expect(registrations).toBe(1);
});

it('requires successful GET-first reconciliation before explicit same-key replay',async()=>{
 let registrations=0;
 call.mockImplementation(async op=>op==='list_grades'?grades:op==='register'?(registrations++,unavailable):registrations?unavailable:anonymous);
 render(<AccountPage/>);await enter('register');
 const retry=await screen.findByRole('button',{name:'Повторить тот же запрос'});
 await waitFor(()=>expect((retry as HTMLButtonElement).disabled).toBe(false));
 fireEvent.click(retry);
 await waitFor(()=>expect(call.mock.calls.filter(([op])=>op==='get_me').length).toBe(3));
 expect(registrations).toBe(1);
});
