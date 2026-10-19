import {test,expect} from '@playwright/test';
import {readFileSync} from 'node:fs';

// Synthetic accounts only. No private traces, cookie attachments or screenshots.
test.use({trace:'off',screenshot:'off'});

test('Identity migration: registration, real grade IDs, all onboarding choices and logout',async({page})=>{
 await page.goto('/account/');
 await expect(page.getByRole('heading',{name:'Вход',exact:true})).toBeVisible();
 await expect(page.getByRole('status')).toHaveText('');
 await page.getByRole('button',{name:'Регистрация',exact:true}).click();
 await expect(page.getByLabel('Имя пользователя',{exact:true})).toHaveAttribute('maxlength','30');
 await page.getByLabel('Имя пользователя',{exact:true}).fill('migration_'+crypto.randomUUID().slice(0,12));
 await page.getByLabel('Пароль',{exact:true}).fill('Qm9!Vx2#Lr7@Zh4%');
 const registered=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/v1/auth/register/');
 await page.getByRole('button',{name:'Зарегистрироваться',exact:true}).click();
 expect((await registered).status()).toBe(201);
 await expect(page.getByRole('heading',{name:'Ваш профиль'})).toBeVisible();
 const grade=await page.locator('#onboarding-grade option').nth(1).getAttribute('value');expect(grade).toMatch(/^[1-9]\d*$/);
 for(const [label,mode]of [['Начать с начала','START_ZERO'],['Самооценка','SELF_REPORT'],['Выбрать диагностику','DIAGNOSTIC']] as const){
  await page.getByLabel('Класс для начала занятий',{exact:true}).selectOption(grade!);
  await page.getByRole('radio',{name:label,exact:true}).check();
  const saved=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/v1/onboarding/complete/');
  await page.getByRole('button',{name:'Сохранить начальную настройку',exact:true}).click();
  const result=await saved;expect(result.status()).toBe(200);expect((await result.json()).data.onboarding_mode).toBe(mode);
  await expect(page.getByRole('status')).toHaveText('Сохранённое состояние загружено.');
 }
 await page.getByRole('button',{name:'Выйти',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Вход',exact:true})).toBeVisible();
 await expect(page.getByLabel('Пароль',{exact:true})).toHaveValue('');
 await expect(page.getByLabel('Имя пользователя',{exact:true})).toHaveAttribute('maxlength','150');
});

test('Identity migration: unknown unsafe login outcome reconciles GET without automatic POST retry',async({page})=>{
 await page.goto('/account/');await expect(page.getByRole('heading',{name:'Вход',exact:true})).toBeVisible();
 let writes=0;
 await page.route('**/api/v1/auth/login/',route=>{writes++;return route.abort();});
 await page.getByLabel('Имя пользователя',{exact:true}).fill('syntheticAbsent');
 await page.getByLabel('Пароль',{exact:true}).fill('Qm9!Vx2#Lr7@Zh4%');
 await page.getByRole('button',{name:'Войти',exact:true}).click();
 await expect(page.getByLabel('Пароль',{exact:true})).toHaveValue('');
 await expect(page.getByRole('status')).toHaveText('Войдите или зарегистрируйтесь.');
 expect(writes).toBe(1);
 await expect(page.getByRole('button',{name:'Повторить тот же запрос'})).toHaveCount(0);
});

test('Identity migration: real staff group creation, history and guarded deletion',async({page,context})=>{
 const input=JSON.parse(readFileSync(process.env.MATHSTART_STAFF_COOKIE_FILE!,'utf8'));
 await context.addCookies(Array.isArray(input)?input:input.cookies);
 await page.goto('/admin/auth/group/add/');
 await page.getByLabel('Название',{exact:true}).fill('migration_'+crypto.randomUUID());
 const created=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/v1/staff/groups/'&&r.request().method()==='POST');
 await page.getByRole('button',{name:'Сохранить',exact:true}).click();expect((await created).status()).toBe(201);
 await expect(page).toHaveURL(/\/admin\/auth\/group\/\d+\/change\/$/);
 await expect(page.getByRole('status')).toHaveText('Данные загружены.');
 await page.getByRole('link',{name:'История',exact:true}).click();
 await expect(page.getByRole('status')).toHaveText('Данные загружены.');
 await page.getByRole('link',{name:'Удалить',exact:true}).click();
 await page.getByRole('button',{name:'Проверить возможность удаления'}).click();
 await expect(page.getByRole('heading',{name:'Подтверждение удаления'})).toBeVisible();
 await page.getByRole('checkbox',{name:'Подтверждаю удаление показанных записей.'}).check();
 const deleted=page.waitForResponse(r=>/\/api\/v1\/staff\/groups\/\d+\/delete\/$/.test(new URL(r.url()).pathname)&&r.request().method()==='POST');
 await page.getByRole('button',{name:'Удалить',exact:true}).click();expect((await deleted).status()).toBe(200);
 await expect(page).toHaveURL(/\/admin\/auth\/group\/$/);
});

test('Identity migration: anonymous staff mutation is denied before malformed payload',async({request})=>{
 const result=await request.post('/api/v1/staff/users/',{data:'malformed',headers:{'Content-Type':'application/json'}});
 expect(result.status()).toBe(401);expect(result.headers()['cache-control']).toContain('no-store');
 expect((await result.json()).error.code).toBe('AUTHENTICATION_REQUIRED');
});
