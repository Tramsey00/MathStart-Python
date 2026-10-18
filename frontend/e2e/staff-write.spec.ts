import {test,expect,type Page} from '@playwright/test';
import {readFileSync} from 'node:fs';

// Only disposable accounts. Keep passwords/cookies and private screenshots out
// of browser evidence; backend owns the permission and deletion decisions.
test.use({trace:'off',screenshot:'off'});
async function staff(page:Page){
 const file=process.env.MATHSTART_STAFF_COOKIE_FILE;if(!file)throw Error('Owned staff cookie fixture required');
 const input=JSON.parse(readFileSync(file,'utf8'));
 await page.context().addCookies(Array.isArray(input)?input:input.cookies);
}
async function saved(page:Page){await expect(page.getByRole('status')).toHaveText('Данные загружены.');}

test('native staff user create profile roles password history and guarded deletion',async({page,browser})=>{
 await staff(page);
 const username='staff_ui_'+crypto.randomUUID().replaceAll('-','');
 const initial='Qm9!Vx2#Lr7@Zh4%',changed='Cp6!Nw3#Fs8@Yk5%';
 await page.goto('/admin/auth/user/add/');
 await page.getByLabel('Имя пользователя',{exact:true}).fill(username);
 await page.getByLabel('Пароль',{exact:true}).fill(initial);
 await page.getByLabel('Повторите пароль',{exact:true}).fill(initial);
 const created=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/v1/staff/users/'&&r.request().method()==='POST');
 await page.getByRole('button',{name:'Сохранить',exact:true}).click();expect((await created).status()).toBe(201);
 await expect(page).toHaveURL(/\/admin\/auth\/user\/\d+\/change\/$/);await saved(page);
 const id=new URL(page.url()).pathname.split('/').at(-3)!;
 await page.getByLabel('Имя',{exact:true}).fill('Проверка');
 await page.getByLabel('Электронная почта',{exact:true}).fill(username+'@example.invalid');
 const group=page.locator('#staff-groups option').first();await expect(group).toBeAttached();
 const groupId=(await group.getAttribute('value'))!;await page.getByLabel('Группы',{exact:true}).selectOption(groupId);
 const permission=page.locator('#staff-user_permissions option').first();await expect(permission).toBeAttached();
 const permissionId=(await permission.getAttribute('value'))!;await page.getByLabel('Прямые права',{exact:true}).selectOption(permissionId);
 await page.getByRole('checkbox',{name:'Подтверждаю изменение профиля, доступа и прав этой записи.'}).check();
 const updated=page.waitForResponse(r=>new URL(r.url()).pathname===`/api/v1/staff/users/${id}/`&&r.request().method()==='PUT');
 await page.getByRole('button',{name:'Сохранить',exact:true}).click();
 const update=await updated;expect(update.status()).toBe(200);const record=(await update.json()).data;
 expect(record.groups.map(String)).toContain(groupId);expect(record.user_permissions.map(String)).toContain(permissionId);
 await saved(page);await expect(page.getByLabel('Имя',{exact:true})).toHaveValue('Проверка');
 await page.getByRole('link',{name:'История',exact:true}).click();await saved(page);
 await expect(page.getByRole('table',{name:'История изменений'})).toBeVisible();
 await expect(page.getByRole('cell',{name:'Изменение',exact:true}).first()).toBeVisible();
 await page.getByRole('link',{name:'Изменить пароль',exact:true}).click();await saved(page);
 await page.getByLabel('Пароль',{exact:true}).fill(changed);
 await page.getByLabel('Повторите пароль',{exact:true}).fill(changed);
 const password=page.waitForResponse(r=>new URL(r.url()).pathname===`/api/v1/staff/users/${id}/password/`&&r.request().method()==='POST');
 await page.getByRole('button',{name:'Сохранить',exact:true}).click();expect((await password).status()).toBe(200);
 await expect(page.getByLabel('Пароль',{exact:true})).toHaveValue('');
 const other=await browser.newContext();
 try{
  const origin=new URL(page.url()).origin;
  const csrf=await other.request.get(origin+'/api/v1/auth/csrf/');expect(csrf.status()).toBe(200);
  const login=await other.request.post(origin+'/api/v1/auth/login/',{data:{username,password:changed},headers:{Origin:origin,'X-CSRFToken':(await csrf.json()).data.csrf_token}});
  expect(login.status()).toBe(200);expect((await login.json()).data.username).toBe(username);
  expect((await other.request.get(origin+'/api/v1/staff/users/')).status()).toBe(403);
  await page.getByRole('link',{name:'Удалить',exact:true}).click();
  await page.getByRole('button',{name:'Проверить возможность удаления'}).click();
  await expect(page.getByRole('heading',{name:'Подтверждение удаления'})).toBeVisible();
  await expect(page.getByRole('button',{name:'Удалить',exact:true})).toBeDisabled();
  const preview=await page.request.get(origin+`/api/v1/staff/users/${id}/delete/`);
  expect(preview.status()).toBe(200);const protectedState=(await preview.json()).data;expect(protectedState.protected).toBe(true);
  const staffCsrf=await page.request.get(origin+'/api/v1/auth/csrf/');expect(staffCsrf.status()).toBe(200);
  const refused=await page.request.post(origin+`/api/v1/staff/users/${id}/delete/`,{data:{ids:[Number(id)],confirmation_token:protectedState.confirmation_token},headers:{Origin:origin,'X-CSRFToken':(await staffCsrf.json()).data.csrf_token}});
  expect(refused.status()).toBe(409);expect((await refused.json()).error.code).toBe('STATE_CONFLICT');
  expect((await other.request.get(origin+'/api/v1/users/me/')).status()).toBe(200);
  await page.getByRole('link',{name:'Изменить',exact:true}).click();await saved(page);
  await page.getByRole('checkbox',{name:'Доступ к администрированию',exact:true}).check();
  await page.getByRole('checkbox',{name:'Подтверждаю изменение профиля, доступа и прав этой записи.'}).check();
  const promoted=page.waitForResponse(r=>new URL(r.url()).pathname===`/api/v1/staff/users/${id}/`&&r.request().method()==='PUT');
  await page.getByRole('button',{name:'Сохранить',exact:true}).click();expect((await promoted).status()).toBe(200);await saved(page);
  const ownPage=await other.newPage();await ownPage.goto(origin+'/admin/password_change/');
  await expect(ownPage.getByLabel('Текущий пароль',{exact:true})).toBeVisible();
  const ownPassword='Jq8!Rm4#Ts7@Uz2%';
  for(const [old,status]of [['wrong-current-password',400],[changed,200]] as const){
   await ownPage.getByLabel('Текущий пароль',{exact:true}).fill(old);
   await ownPage.getByLabel('Новый пароль',{exact:true}).fill(ownPassword);
   await ownPage.getByLabel('Повторите новый пароль',{exact:true}).fill(ownPassword);
   const priorCookies=await other.cookies();
   const ownSaved=ownPage.waitForResponse(r=>new URL(r.url()).pathname==='/api/v1/staff/password_change/'&&r.request().method()==='POST');
   await ownPage.getByRole('button',{name:'Сохранить',exact:true}).click();expect((await ownSaved).status()).toBe(status);
   if(status===400){
    await expect(ownPage.getByLabel('Текущий пароль',{exact:true})).toHaveValue('');
    await expect(ownPage.getByLabel('Новый пароль',{exact:true})).toHaveValue('');
    await expect(ownPage.getByLabel('Повторите новый пароль',{exact:true})).toHaveValue('');
    expect((await other.request.get(origin+'/api/v1/users/me/')).status()).toBe(200);
   }else{
    await expect(ownPage).toHaveURL(/\/admin\/password_change\/done\/$/);
    await expect(ownPage.getByRole('heading',{name:'Пароль изменён'})).toBeVisible();
    expect((await other.request.get(origin+'/api/v1/users/me/')).status()).toBe(200);
    const stale=await browser.newContext();
    try{await stale.addCookies(priorCookies);expect((await stale.request.get(origin+'/api/v1/users/me/')).status()).toBe(401);}finally{await stale.close();}
   }
  }
  await page.getByRole('checkbox',{name:'Активен',exact:true}).uncheck();
  await page.getByRole('checkbox',{name:'Подтверждаю изменение профиля, доступа и прав этой записи.'}).check();
  const deactivated=page.waitForResponse(r=>new URL(r.url()).pathname===`/api/v1/staff/users/${id}/`&&r.request().method()==='PUT');
  await page.getByRole('button',{name:'Сохранить',exact:true}).click();expect((await deactivated).status()).toBe(200);await saved(page);
  expect((await other.request.get(origin+'/api/v1/users/me/')).status()).toBe(401);
  // A native staff-created account without a profile/receipt remains deletable.
  await page.goto('/admin/auth/user/add/');
  await page.getByLabel('Имя пользователя',{exact:true}).fill(username+'_deletable');
  await page.getByLabel('Пароль',{exact:true}).fill(initial);await page.getByLabel('Повторите пароль',{exact:true}).fill(initial);
  const unprotectedCreated=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/v1/staff/users/'&&r.request().method()==='POST');
  await page.getByRole('button',{name:'Сохранить',exact:true}).click();expect((await unprotectedCreated).status()).toBe(201);
  await expect(page).toHaveURL(/\/admin\/auth\/user\/\d+\/change\/$/);await saved(page);
  const deletableId=new URL(page.url()).pathname.split('/').at(-3)!;
  await page.getByRole('link',{name:'Удалить',exact:true}).click();
  await page.getByRole('button',{name:'Проверить возможность удаления'}).click();
  await expect(page.getByRole('heading',{name:'Подтверждение удаления'})).toBeVisible();
  await page.getByRole('checkbox',{name:'Подтверждаю удаление показанных записей.'}).check();
  const deleted=page.waitForResponse(r=>new URL(r.url()).pathname===`/api/v1/staff/users/${deletableId}/delete/`&&r.request().method()==='POST');
  await page.getByRole('button',{name:'Удалить',exact:true}).click();expect((await deleted).status()).toBe(200);
  await expect(page).toHaveURL(/\/admin\/auth\/user\/$/);await saved(page);
  expect((await page.request.get(origin+`/api/v1/staff/users/${deletableId}/`)).status()).toBe(404);
 }finally{await other.close();}
});

test('native group delete-selected previews and removes the complete selected set',async({page})=>{
 await staff(page);const names=[0,1].map(i=>'bulk_ui_'+crypto.randomUUID()+'_'+i);
 for(const name of names){
  await page.goto('/admin/auth/group/add/');await page.getByLabel('Название',{exact:true}).fill(name);
  const created=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/v1/staff/groups/'&&r.request().method()==='POST');
  await page.getByRole('button',{name:'Сохранить',exact:true}).click();expect((await created).status()).toBe(201);
  await expect(page).toHaveURL(/\/admin\/auth\/group\/\d+\/change\/$/);await saved(page);
 }
 await page.goto('/admin/auth/group/');await saved(page);
 for(const name of names)await page.getByRole('checkbox',{name:'Выбрать '+name,exact:true}).check();
 const preview=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/v1/staff/groups/delete_selected/'&&r.request().method()==='GET');
 await page.getByRole('button',{name:'Удалить выбранные',exact:true}).click();const previewResponse=await preview;expect(previewResponse.status()).toBe(200);const ids=(await previewResponse.json()).data.ids;expect(ids).toHaveLength(2);
 await page.getByRole('checkbox',{name:'Подтверждаю удаление показанных записей.'}).check();
 const deleted=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/v1/staff/groups/delete_selected/'&&r.request().method()==='POST');
 await page.getByRole('button',{name:'Удалить',exact:true}).click();const result=await deleted;expect(result.status()).toBe(200);
 await expect(page).toHaveURL(/\/admin\/auth\/group\/$/);await saved(page);
 for(const id of ids)expect((await page.request.get(`/api/v1/staff/groups/${id}/`)).status()).toBe(404);
 for(const name of names)await expect(page.getByRole('checkbox',{name:'Выбрать '+name,exact:true})).toHaveCount(0);
});
