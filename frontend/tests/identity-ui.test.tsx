import {afterEach,describe,it,expect,vi} from 'vitest';
import {render,screen,fireEvent,cleanup} from '@testing-library/react';
const mocks=vi.hoisted(()=>({call:vi.fn(),refresh:vi.fn()}));
vi.mock('../src/features/identity/session',()=>({api:{call:mocks.call},useSession:()=>({refresh:mocks.refresh}),safeReturn:()=>'/account/'}));
import {AuthForm} from '../src/features/identity/auth-form';
afterEach(()=>{cleanup();vi.clearAllMocks();});
describe('MS-T009 shared auth form',()=>{
 it('uses generic login error, autocomplete and clears the password',async()=>{
  mocks.call.mockResolvedValue({ok:false,error:{code:'AUTHENTICATION_REQUIRED',outcome:'rejected'}});
  render(<AuthForm/>);
  fireEvent.change(screen.getByLabelText('Логин'),{target:{value:'student'}});
  const password=screen.getByLabelText('Пароль') as HTMLInputElement;
  expect(password.autocomplete).toBe('current-password');
  fireEvent.change(password,{target:{value:'synthetic wrong password'}});
  fireEvent.click(screen.getByRole('button',{name:'Войти',exact:true}));
  await screen.findByText('Неверный логин или пароль');expect(password.value).toBe('');
 });
 it('reconciles unknown outcome and prevents blind resubmission',async()=>{
  mocks.call.mockResolvedValue({ok:false,error:{code:'NETWORK_ERROR',outcome:'unknown'}});mocks.refresh.mockResolvedValue(undefined);
  render(<AuthForm register/>);
  fireEvent.change(screen.getByLabelText('Логин'),{target:{value:'student'}});
  fireEvent.change(screen.getByLabelText('Пароль'),{target:{value:'A synthetic phrase! 2026'}});
  fireEvent.click(screen.getByRole('button',{name:'Создать аккаунт'}));
  await screen.findByText(/Не удалось подтвердить результат/);
  expect(mocks.refresh).toHaveBeenCalledTimes(1);
  fireEvent.click(screen.getByRole('button',{name:'Создать аккаунт'}));
  expect(mocks.call).toHaveBeenCalledTimes(1);
 });
 it('honors Retry-After and does not retry automatically',async()=>{
  mocks.call.mockResolvedValue({ok:false,error:{code:'RATE_LIMITED',message:'Подождите.',outcome:'rejected',retryAfterSeconds:30}});
  render(<AuthForm/>);fireEvent.change(screen.getByLabelText('Логин'),{target:{value:'student'}});fireEvent.change(screen.getByLabelText('Пароль'),{target:{value:'synthetic'}});
  fireEvent.click(screen.getByRole('button',{name:'Войти',exact:true}));
  await screen.findByText(/Повторите через 30 с/);expect(screen.getByRole('button',{name:'Войти',exact:true}).matches(':disabled')).toBe(true);
  expect(mocks.call).toHaveBeenCalledTimes(1);
 });
});
