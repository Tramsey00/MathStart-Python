import {useLayoutEffect, useRef, type ReactNode} from 'react';

// Only one mode is mounted. Height follows measured content, never a guessed
// login/register height, so validation, font loading and wrapping still fit.
export function AuthModeTransition({mode,children}:{mode:string|null;children:ReactNode}){
 const frame=useRef<HTMLDivElement>(null),body=useRef<HTMLDivElement>(null);
 const mounted=useRef(false),restoreFocus=useRef(false);
 useLayoutEffect(()=>{
  const outer=frame.current!,inner=body.current!;
  const motion=matchMedia('(prefers-reduced-motion: reduce)');
  let heightAnimation:Animation|undefined,contentAnimation:Animation|undefined,target=-1;
  const first=!mounted.current;mounted.current=true;
  function resize(animate:boolean){
   const next=inner.getBoundingClientRect().height;
   if(Math.abs(next-target)<.5)return;
   const from=outer.getBoundingClientRect().height;
   heightAnimation?.cancel();target=next;outer.style.height=`${next}px`;
   if(animate&&!motion.matches&&Math.abs(next-from)>.5){
    heightAnimation=outer.animate([{height:`${from}px`},{height:`${next}px`}],{duration:220,easing:'cubic-bezier(.4,0,.2,1)'});
   }
  }
  resize(!first);
  if(!first&&!motion.matches)contentAnimation=inner.animate([{opacity:.3,transform:'translateY(4px)'},{opacity:1,transform:'translateY(0)'}],{duration:200,easing:'cubic-bezier(.22,1,.36,1)'});
  if(restoreFocus.current){inner.querySelector<HTMLElement>('h1')?.focus({preventScroll:true});restoreFocus.current=false;}
  const observer=new ResizeObserver(()=>resize(true));observer.observe(inner);
  const stop=()=>{if(motion.matches){heightAnimation?.cancel();contentAnimation?.cancel();}};
  motion.addEventListener('change',stop);
  return()=>{
   restoreFocus.current=inner.contains(document.activeElement)||(document.activeElement===document.body&&restoreFocus.current);
   // Freeze the displayed height before cancelling: rapid mode switches start
   // at this frame, rather than snapping to an old animation's endpoint.
   outer.style.height=`${outer.getBoundingClientRect().height}px`;
   heightAnimation?.cancel();contentAnimation?.cancel();observer.disconnect();motion.removeEventListener('change',stop);
  };
 },[mode]);
 return <div className="auth-mode-frame" ref={frame}><div className="auth-mode-content" key={mode} ref={body}
  onFocusCapture={()=>{restoreFocus.current=true;}}
  onBlurCapture={event=>{if(event.relatedTarget&&!event.currentTarget.contains(event.relatedTarget as Node))restoreFocus.current=false;}}
 >{children}</div></div>;
}
