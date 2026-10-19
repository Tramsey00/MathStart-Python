import {it,expect,vi} from 'vitest';
import {render,screen,fireEvent,within} from '@testing-library/react';
import inventory from '../../docs/acceptance/MS7-MIG-R01/admin-inventory.json';
import {StaffList,StaffDetails,StaffHistory,staffColumns,staffLabel} from '../src/shared/ui/staff-records';

const models:Record<string,string>={'auth.Group':'groups','auth.User':'users','content.ContentPage':'pages','content.Grade':'grades','content.LessonPublication':'publications','content.MediaAsset':'media_assets','content.Redirect':'redirects','content.Section':'sections','content.Subject':'subjects'};
it.each(inventory.registered)('preserves every native list column for $model',entry=>{
 const resource=models[entry.model]!;
 const expected=entry.list_display.map(field=>field==='__str__'?'name':['grade','subject','section','page','related_page'].includes(field)?field+'_id':field);
 expect(staffColumns[resource]).toEqual(expected);
 const row=Object.fromEntries(expected.map((field,index)=>[field,field.startsWith('is_')?false:field.endsWith('_id')?9223372036854775807n:'value '+index]));
 render(<StaffList resource={resource} rows={[{...row,id:9223372036854775807n}]} base="/admin/example/" caption="Записи"/>);
 expect(screen.getAllByRole('columnheader').map(node=>node.textContent)).toEqual(expected.map(staffLabel));
 expect(screen.getByRole('link').getAttribute('href')).toBe('/admin/example/9223372036854775807/change/');
});
it('shows full user columns and preserves exact bulk selection without rounding',()=>{
 const change=vi.fn(),id='9223372036854775807';
 render(<StaffList resource="users" rows={[{id:BigInt(id),username:'<script>safe</script>',email:'synthetic@example.invalid',first_name:'Имя',last_name:'Фамилия',is_staff:false}]} base="/admin/auth/user/" caption="Пользователи" selection={{ids:[id],disabled:false,change}}/>);
 const row=screen.getAllByRole('row')[1]!;
 expect(within(row).getByText('synthetic@example.invalid')).toBeTruthy();
 expect(within(row).getByText('Нет')).toBeTruthy();
 expect(document.querySelector('script')).toBeNull();
 const checkbox=screen.getByRole('checkbox',{name:'Выбрать <script>safe</script>'});
 expect((checkbox as HTMLInputElement).checked).toBe(true);
 fireEvent.click(checkbox);expect(change).toHaveBeenCalledWith(id,false);
 expect(screen.getByRole('region',{name:'Пользователи'}).getAttribute('tabindex')).toBe('0');
});
it('escapes authored HTML in read-only details and describes booleans and nulls',()=>{
 render(<StaffDetails record={{title:'<img src=x onerror=alert(1)>',body_html:'<p>raw source</p>',is_published:false,grade_id:9223372036854775807n,section_id:null}}/>);
 expect(document.querySelector('img,p')).toBeNull();
 expect(screen.getByText('<p>raw source</p>')).toBeTruthy();
 expect(screen.getByText('Нет')).toBeTruthy();
 expect(screen.getByText('№ 9223372036854775807')).toBeTruthy();
 expect(screen.getByText('—')).toBeTruthy();
});
it('presents history actions with dates, exact actors and escaped summaries',()=>{
 render(<StaffHistory rows={[{id:1n,actor_id:9223372036854775807n,object_id:'9007199254740993',action:'CHANGE',occurred_at:'2026-10-18T00:00:00Z',summary:'Changed.'}]}/>);
 expect(screen.getByRole('table',{name:'История изменений'})).toBeTruthy();
 expect(screen.getByText('Изменение')).toBeTruthy();expect(screen.getByText('Запись изменена.')).toBeTruthy();
 expect(screen.getByText('№ 9223372036854775807')).toBeTruthy();
 expect(screen.getByText('№ 9007199254740993')).toBeTruthy();
 expect(screen.getByText('2026-10-18T00:00:00Z')).toBeTruthy();
});
