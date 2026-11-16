import {type FormEvent} from 'react';
import {PasswordField} from './auth-form';

export function PasswordChangeForm({disabled,onSubmit}:{disabled:boolean;onSubmit:(event:FormEvent<HTMLFormElement>)=>void}){
 return <form className="password-change-form" onSubmit={onSubmit}><fieldset disabled={disabled}>
  <PasswordField name="current_password" label="Текущий пароль"/>
  <div className="password-new-group"><PasswordField name="new_password" label="Новый пароль" fresh/>
  <PasswordField name="confirm_password" label="Повторите новый пароль" fresh showHint={false}/></div>
  <button className="identity-button" type="submit">Сменить пароль</button>
 </fieldset></form>;
}
