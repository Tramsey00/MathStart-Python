import {it,expect,vi} from 'vitest';
import {render,screen,fireEvent,waitFor} from '@testing-library/react';
const {call}=vi.hoisted(()=>({call:vi.fn()}));
vi.mock('../src/shared/api/staff-write-client',()=>({createStaffWriteClient:()=>({call})}));
vi.mock('react-router',()=>({useLocation:()=>({pathname:'/admin/auth/user/2/change/'})}));
import StaffPage from '../src/app/routes/staff-write';

it('allows existing blank profile fields while preserving username, dates and explicit confirmation',async()=>{
 const record={id:2,username:'syntheticStudent',first_name:'',last_name:'',email:'',is_active:true,is_staff:false,is_superuser:false,last_login:null,date_joined:'2026-10-17T00:00:00Z',groups:[],user_permissions:[],has_usable_password:true};
 call.mockImplementation(async op=>({ok:true,value:{data:op==='staff_get_users'?record:[],meta:{}}}));
 render(<StaffPage/>);
 await waitFor(()=>expect((screen.getByLabelText('Имя пользователя') as HTMLInputElement).value).toBe('syntheticStudent'));
 for(const label of ['Имя','Фамилия','Электронная почта'])expect((screen.getByLabelText(label) as HTMLInputElement).required).toBe(false);
 const form=screen.getByLabelText('Имя пользователя').closest('form')!;
 expect(form.checkValidity()).toBe(false);
 fireEvent.click(screen.getByRole('checkbox',{name:'Подтверждаю изменение профиля, доступа и прав этой записи.'}));
 expect(form.checkValidity()).toBe(true);
});
