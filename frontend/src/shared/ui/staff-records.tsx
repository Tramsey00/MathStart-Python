import type {ReactNode} from 'react';

// Native list_display fields, mapped to the closed target DTO. Relations remain
// exact identifiers: fetching labels must never require broader permissions.
export const staffColumns:Record<string,readonly string[]>={
 groups:['name'], users:['username','email','first_name','last_name','is_staff'],
 grades:['title','slug','order'], subjects:['title','grade_id','slug','order'],
 sections:['title','subject_id','slug','order'],
 pages:['title','page_type','grade_id','subject_id','section_id','order','is_published','updated_at'],
 publications:['page_id','source_path','published_at'],
 media_assets:['title','file','related_page_id'], redirects:['old_path','new_path','is_permanent','is_active'],
};
const labels:Record<string,string>={ids:'Идентификаторы записей',selected:'Выбранные записи',protected:'Есть защищённые связи',id:'Идентификатор',title:'Название',name:'Название',slug:'Адрес',order:'Порядок',description:'Описание',username:'Имя пользователя',email:'Электронная почта',first_name:'Имя',last_name:'Фамилия',is_staff:'Доступ к администрированию',is_superuser:'Суперпользователь',is_active:'Активен',last_login:'Последний вход',date_joined:'Дата регистрации',groups:'Группы',user_permissions:'Прямые права',permissions:'Права',has_usable_password:'Вход по паролю доступен',grade_id:'Класс',subject_id:'Предмет',section_id:'Раздел',page_id:'Страница',related_page_id:'Связанная страница',page_type:'Тип страницы',is_published:'Опубликовано',body_html:'Содержимое HTML',page_css:'Стили страницы',page_js:'Сценарий страницы',seo_title:'Заголовок SEO',seo_description:'Описание SEO',source_location:'Расположение исходника',source_path:'Путь исходника',published_digest:'Контрольная сумма публикации',published_at:'Дата публикации',created_at:'Дата создания',updated_at:'Дата изменения',file:'Файл',alt_text:'Альтернативный текст',old_path:'Исходный адрес',new_path:'Новый адрес',is_permanent:'Постоянное перенаправление',actor_id:'Пользователь',object_id:'Объект',action:'Действие',occurred_at:'Дата',summary:'Описание',publication:'Публикация',operation_id:'Операция',release_id:'Версия',phase:'Состояние',pending:'Ожидает завершения',active:'Активная версия',namespace:'Область',generation:'Поколение',fence_generation:'Поколение блокировки',manifest_digest:'Контрольная сумма манифеста',plan_digest:'Контрольная сумма плана',owner_id:'Владелец операции',lease_until:'Срок аренды',lease_expires_at:'Срок аренды',error_code:'Код ошибки'};
export function staffLabel(field:string){return labels[field]??field;}
type RecordData=Record<string,unknown>;
function Value({value,field,unbroken=false}:{value:unknown;field?:string;unbroken?:boolean}){
 if(value===null||value===undefined||value==='')return <>—</>;
 if(typeof value==='boolean')return <>{value?'Да':'Нет'}</>;
 if(Array.isArray(value))return value.length?<ul>{value.map((item,index)=><li key={index}><Value value={item}/></li>)}</ul>:<>Нет</>;
 if(typeof value==='object')return <StaffDetails record={value as RecordData}/>;
 const text=String(value);
 if(field==='action')return <>{({ADD:'Добавление',CHANGE:'Изменение',DELETE:'Удаление'} as Record<string,string>)[text]??text}</>;
 if(field==='summary'){
  const deletion=/^Delete (\d+) records\.$/.exec(text);
  return <>{deletion?'Будет удалено записей: '+deletion[1]:({'Added.':'Запись добавлена.','Changed.':'Запись изменена.','Deleted.':'Запись удалена.','Protected related records prevent deletion.':'Защищённые связанные записи не позволяют удалить выбранные объекты.'} as Record<string,string>)[text]??text}</>;
 }
 if(field?.endsWith('_id'))return <span style={{whiteSpace:unbroken?'nowrap':'normal'}}>№ {text}</span>;
 if(unbroken&&(field?.endsWith('_at')||field==='last_login'||field==='date_joined'))return <span style={{whiteSpace:'nowrap'}}>{text}</span>;
 return <>{text}</>;
}
export function StaffDetails({record}:{record:RecordData}){
 return <dl>{Object.entries(record).map(([field,value])=><div key={field}><dt>{staffLabel(field)}</dt><dd style={{whiteSpace:'pre-wrap',overflowWrap:'anywhere'}}><Value field={field} value={value}/></dd></div>)}</dl>;
}
const cellStyle={padding:'.5rem',textAlign:'left',verticalAlign:'top',whiteSpace:'nowrap',borderBottom:'1px solid var(--ms-ui-border)'} as const;
const headingStyle={...cellStyle,whiteSpace:'nowrap'} as const;
function Table({caption,children}:{caption:string;children:ReactNode}){
 return <div role="region" aria-label={caption} tabIndex={0} style={{overflowX:'auto',maxWidth:'100%'}}><table style={{width:'100%',borderCollapse:'collapse'}}><caption style={{textAlign:'left',paddingBlock:'.5rem'}}>{caption}</caption>{children}</table></div>;
}
export function StaffList({resource,rows,base,caption,selection}:{resource:string;rows:RecordData[];base:string;caption:string;selection?:{ids:string[];disabled:boolean;change:(id:string,checked:boolean)=>void}}){
 const columns=staffColumns[resource]??['id'];
 if(!rows.length)return <p>Записей нет.</p>;
 return <Table caption={caption}><thead><tr>{selection&&<th scope="col" style={headingStyle}>Выбор</th>}{columns.map(field=><th scope="col" key={field} style={headingStyle}>{staffLabel(field)}</th>)}</tr></thead><tbody>{rows.map(row=>{const id=String(row.id),name=String(row.username??row.name??row.title??row.source_path??row.old_path??id);return <tr key={id}>{selection&&<td style={cellStyle}><input type="checkbox" aria-label={'Выбрать '+name} checked={selection.ids.includes(id)} disabled={selection.disabled} onChange={e=>selection.change(id,e.target.checked)}/></td>}{columns.map((field,index)=>index===0?<th scope="row" style={cellStyle} key={field}><a href={base+id+'/change/'}><Value field={field} value={row[field]} unbroken/></a></th>:<td style={cellStyle} key={field}><Value field={field} value={row[field]} unbroken/></td>)}</tr>;})}</tbody></Table>;
}
export function StaffHistory({rows}:{rows:RecordData[]}){
 const columns=['occurred_at','actor_id','action','object_id','summary'];
 if(!rows.length)return <p>История изменений пуста.</p>;
 return <Table caption="История изменений"><thead><tr>{columns.map(field=><th scope="col" style={headingStyle} key={field}>{staffLabel(field)}</th>)}</tr></thead><tbody>{rows.map(row=><tr key={String(row.id)}>{columns.map(field=><td style={cellStyle} key={field}><Value field={field} value={row[field]} unbroken/></td>)}</tr>)}</tbody></Table>;
}
