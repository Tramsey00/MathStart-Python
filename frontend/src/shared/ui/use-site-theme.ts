import { useEffect, useState, type SetStateAction } from 'react';

export function useSiteTheme() {
  // The first client render must agree with SSG, independent of browser storage.
  const [dark, setDark] = useState(false);
  useEffect(() => {
    const system=matchMedia('(prefers-color-scheme: dark)');
    const sync=()=>{
      let saved:string|null=null;try{saved=localStorage.getItem('mathstart-mode');}catch{/* Storage is optional. */}
      const next=saved==='dark'||saved!=='light'&&system.matches;
      document.documentElement.dataset.theme=next?'dark':'light';setDark(next);
    };
    const local=()=>setDark(document.documentElement.dataset.theme==='dark');
    sync();system.addEventListener('change',sync);window.addEventListener('storage',sync);window.addEventListener('mathstart-theme-change',local);
    return()=>{system.removeEventListener('change',sync);window.removeEventListener('storage',sync);window.removeEventListener('mathstart-theme-change',local);};
  }, []);
  function setTheme(value:SetStateAction<boolean>){
    const next=typeof value==='function'?value(dark):value;
    document.documentElement.dataset.theme=next?'dark':'light';
    try{localStorage.setItem('mathstart-mode',next?'dark':'light');}catch{/* Storage is optional. */}
    setDark(next);window.dispatchEvent(new Event('mathstart-theme-change'));
  }
  return [dark, setTheme] as const;
}
