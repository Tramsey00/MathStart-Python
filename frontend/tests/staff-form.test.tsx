import {it,expect,vi} from 'vitest';
import {render,screen,fireEvent,waitFor} from '@testing-library/react';
const {call,location,grants}=vi.hoisted(()=>({call:vi.fn(),location:{pathname:'/admin/auth/user/2/change/'},grants:{view:true,add:true,change:true,delete:true}}));
vi.mock('../src/shared/api/staff-write-client',()=>({createStaffWriteClient:()=>({call})}));
vi.mock('../src/shared/ui/staff-workspace',()=>({staffResources:[['users','auth/user','Пользователи'],['groups','auth/group','Группы']],StaffHeading:({title}:{title:string})=><h1>{title}</h1>,useStaffCapabilities:()=>({version:1,own_password:true,resources:Object.fromEntries(['grades','subjects','sections','pages','publications','media_assets','redirects','users','groups'].map(name=>[name,grants]))})}));
vi.mock('react-router',()=>({useLocation:()=>location,useNavigate:()=>vi.fn(),Link:({to,...props}:any)=><a href={to} {...props}/>}));
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
 expect(screen.getByRole('heading',{name:'Смена пароля'})).toBeTruthy();
 expect(screen.getByText(/нет подтверждённого результата/)).toBeTruthy();
 expect(screen.queryByLabelText('Текущий пароль')).toBeNull();
 expect(call).not.toHaveBeenCalled();
 location.pathname='/admin/auth/user/2/change/';
});

it('keeps the draft and its original revision after 409 without retrying or rereading',async()=>{
 const record={id:2,username:'syntheticStudent',first_name:'Original',last_name:'',email:'',is_active:true,is_staff:false,is_superuser:false,last_login:null,date_joined:'2026-10-17T00:00:00Z',groups:[],user_permissions:[],has_usable_password:true,expected_revision:'original-revision'};
 call.mockClear();call.mockImplementation(async op=>op==='update_staff_users'?{ok:false,error:{status:409,code:'STATE_CONFLICT',message:'Запись уже изменена.',outcome:'rejected'}}:{ok:true,value:{data:op==='staff_get_users'?record:[],meta:{}}});
 render(<StaffPage/>);
 await waitFor(()=>expect((screen.getByLabelText('Имя') as HTMLInputElement).value).toBe('Original'));
 await waitFor(()=>expect(screen.getByRole('button',{name:'Сохранить'}).closest('fieldset')!.disabled).toBe(false));
 fireEvent.change(screen.getByLabelText('Имя'),{target:{value:'Unsaved draft'}});
 fireEvent.submit(screen.getByLabelText('Имя').closest('form')!);
 await screen.findByText('Запись уже изменена.');
 expect((screen.getByLabelText('Имя') as HTMLInputElement).value).toBe('Unsaved draft');
 expect(call.mock.calls.filter(([op])=>op==='update_staff_users')).toEqual([['update_staff_users',expect.objectContaining({body:expect.objectContaining({first_name:'Unsaved draft',expected_revision:'original-revision'})})]]);
 expect(call.mock.calls.filter(([op])=>op==='staff_get_users')).toHaveLength(1);
});
