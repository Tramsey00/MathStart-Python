import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode, Ref } from "react";
export function Button({ type="button", ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return <button {...props} type={type} className={["ms-ui-button",props.className].filter(Boolean).join(" ")} />;
}
type FieldProps=InputHTMLAttributes<HTMLInputElement> & {
  id:string; label:string; help?:string; error?:string; errorVisible?:boolean; inputRef?:Ref<HTMLInputElement>;
};
export function Field({id,label,help="",error="",errorVisible=Boolean(error),inputRef,required,...props}:FieldProps) {
  return <div className="ms-ui-field">
    <label htmlFor={id}>{label}{required && <> <span>(обязательно)</span></>}</label>
    <p id={id+"-help"} className="ms-ui-muted">{help}</p>
    <input autoComplete="off" name={id} type="text" {...props} ref={inputRef} id={id} required={required}
      aria-invalid={errorVisible} aria-describedby={id+"-help "+id+"-error"} />
    <p id={id+"-error"} className="ms-ui-field-error" hidden={!errorVisible}>{error}</p>
  </div>;
}
export function Card({title,children}:{title:string;children:ReactNode}) {
  return <article className="ms-ui-card"><h3>{title}</h3><p>{children}</p></article>;
}
export type ViewState="ordinary"|"loading"|"error"|"empty";
export function State({state,title,children}:{state:ViewState;title:string;children:ReactNode}) {
  return <section className="ms-ui-state" data-state={state} aria-label={title} aria-busy={state==="loading"?true:undefined}>
    <h3>{title}</h3><p>{children}</p>
  </section>;
}
export function SkipLink({target,children}:{target:string;children:ReactNode}) {
  return <a className="ms-ui-skip" href={"#"+target}>{children}</a>;
}
