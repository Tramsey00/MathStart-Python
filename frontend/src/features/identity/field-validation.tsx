import {createContext,useContext,useId,useLayoutEffect,useRef,useState,type ComponentProps,type FormEvent} from 'react';

const Errors=createContext<Record<string,string>>({});
export const useFieldError=(id:string)=>useContext(Errors)[id];
export function FieldError({id}:{id:string}){
 const error=useFieldError(id);
 return error?<p id={id+'-error'} className="field-error" role="alert">{error}</p>:null;
}
export function ValidationInput({id:givenId,...props}:ComponentProps<'input'>){
 const generated=useId(),id=givenId??generated,error=useFieldError(id);
 return <><input {...props} id={id} aria-invalid={error?true:props['aria-invalid']} aria-describedby={[props['aria-describedby'],error?id+'-error':''].filter(Boolean).join(' ')||undefined}/><FieldError id={id}/></>;
}
const missing:Record<string,string>={username:'Введите логин',password:'Введите пароль',current_password:'Введите текущий пароль',new_password:'Введите новый пароль',confirm_password:'Повторите новый пароль',email:'Введите почту для восстановления',grade:'Выберите класс перед сохранением'};
// Radios share one inline error; each control still has its own label and id.
const errorKey=(input:HTMLInputElement)=>input.dataset.validationGroup??input.id;
function message(input:HTMLInputElement){
 const v=input.validity;
 if(v.valueMissing)return missing[input.name]??'Выберите значение';
 if(v.typeMismatch&&input.type==='email')return 'Введите адрес почты в формате name@example.com';
 if(v.tooShort)return `Используйте не менее ${input.minLength} символов`;
 if(v.tooLong)return `Используйте не более ${input.maxLength} символов`;
 if(v.patternMismatch)return 'Проверьте формат значения';
 if(!v.valid)return input.validationMessage;
 if(input.dataset.registrationLogin==='true'&&(!/^[\p{L}\p{N}_@.+-]+$/u.test(input.value)||Array.from(input.value).length>30))return 'Логин: до 30 букв, цифр или символов @ . + - _. Без пробелов.';
 if(input.name==='confirm_password'){
  const next=input.form?.elements.namedItem('new_password');
  if(next instanceof HTMLInputElement&&input.value!==next.value)return 'Пароли не совпадают. Повторите новый пароль.';
 }
 return '';
}
// Native constraint validation still blocks submission. Cancelling only the
// invalid event suppresses its bubble; errors are rendered beside the inputs.
export function ValidationScope({resetKey,...props}:ComponentProps<'div'>&{resetKey?:string|null}){
 const [errors,setErrors]=useState<Record<string,string>>({});
 const root=useRef<HTMLDivElement>(null);
 const pendingFocus=useRef<HTMLInputElement|null>(null);
 useLayoutEffect(()=>{
  // Remove messages left by the former custom-validity implementation (also
  // when HMR preserves the input DOM). ValidityState now supplies the rules.
  root.current?.querySelectorAll('input').forEach(input=>input.setCustomValidity(''));
  setErrors({});pendingFocus.current=null;
 },[resetKey]);
 useLayoutEffect(()=>{pendingFocus.current?.focus();pendingFocus.current=null;},[errors]);
 function invalid(event:FormEvent<HTMLDivElement>){
  const input=event.target;
  if(!(input instanceof HTMLInputElement)||!input.id)return;
  event.preventDefault();
  pendingFocus.current=input.form?.querySelector<HTMLInputElement>('input:invalid')??input;
  setErrors(old=>({...old,[errorKey(input)]:message(input)}));
 }
 function submit(event:FormEvent<HTMLDivElement>){
  const form=event.target;if(!(form instanceof HTMLFormElement))return;
  const inputs=Array.from(form.elements).filter((e):e is HTMLInputElement=>e instanceof HTMLInputElement&&e.willValidate);
  const failures=inputs.map(input=>({input,error:message(input)})).filter(item=>item.error);
  if(!failures.length)return;
  event.preventDefault();event.stopPropagation();
  pendingFocus.current=failures[0].input;
  setErrors(old=>({...old,...Object.fromEntries(failures.map(({input,error})=>[errorKey(input),error]))}));
 }
 function update(event:FormEvent<HTMLDivElement>){
  if(!(event.target instanceof HTMLInputElement))return;
  const input=event.target;
  input.setCustomValidity('');
  setErrors(old=>{
   const next={...old};
   const key=errorKey(input);
   if(key in old){const error=message(input);if(error)next[key]=error;else delete next[key];}
   if(input.name==='new_password'){
    const confirmation=input.form?.elements.namedItem('confirm_password');
    if(confirmation instanceof HTMLInputElement&&confirmation.id in old){const error=message(confirmation);if(error)next[confirmation.id]=error;else delete next[confirmation.id];}
   }
   return next;
  });
 }
 return <Errors.Provider value={errors}><div {...props} ref={root} onInvalidCapture={invalid} onSubmitCapture={submit} onInputCapture={update} onChangeCapture={update} onResetCapture={()=>setErrors({})}/></Errors.Provider>;
}
