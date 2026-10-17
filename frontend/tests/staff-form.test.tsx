import {it,expect,vi} from 'vitest';
import {render,screen,fireEvent,waitFor} from '@testing-library/react';
const {call,location,grants}=vi.hoisted(()=>({call:vi.fn(),location:{pathname:'/admin/auth/user/2/change/'},grants:{view:true,add:true,change:true,delete:true}}));
vi.mock('../src/shared/api/staff-write-client',()=>({createStaffWriteClient:()=>({call})}));
vi.mock('../src/shared/api/staff-capabilities',()=>({readStaffCapabilities:()=>({version:1,own_password:true,resources:Object.fromEntries(['grades','subjects','sections','pages','publications','media_assets','redirects','users','groups'].map(name=>[name,grants]))})}));
vi.mock('react-router',()=>({useLocation:()=>location}));
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

it('hides edit, password and deletion controls from view-only staff',async()=>{
 Object.assign(grants,{view:true,add:false,change:false,delete:false});
 call.mockImplementation(async()=>({ok:true,value:{data:{id:2,username:'syntheticStudent'},meta:{}}}));
 render(<StaffPage/>);
 await screen.findByText(/syntheticStudent/);
 expect(screen.queryByRole('button',{name:'Сохранить'})).toBeNull();
 expect(screen.queryByRole('link',{name:'Изменить'})).toBeNull();
 expect(screen.queryByRole('link',{name:'Изменить пароль'})).toBeNull();
 expect(screen.queryByRole('link',{name:'Удалить'})).toBeNull();
 Object.assign(grants,{view:true,add:true,change:true,delete:true});
});

it('serves the native password completion page without submitting or reading private records',()=>{
 location.pathname='/admin/password_change/done/';call.mockClear();
 render(<StaffPage/>);
 expect(screen.getByRole('heading',{name:'Пароль изменён'})).toBeTruthy();
 expect(screen.queryByLabelText('Текущий пароль')).toBeNull();
 expect(call).not.toHaveBeenCalled();
 location.pathname='/admin/auth/user/2/change/';
});
