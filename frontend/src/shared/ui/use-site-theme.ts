import { useEffect, useState } from 'react';

export function useSiteTheme() {
  const [dark, setDark] = useState(() => {
    try { return localStorage.getItem('mathstart-mode') === 'dark'; } catch { return false; }
  });
  useEffect(() => {
    document.documentElement.dataset.theme = dark ? 'dark' : 'light';
    try { localStorage.setItem('mathstart-mode', dark ? 'dark' : 'light'); } catch { /* Storage is optional. */ }
  }, [dark]);
  return [dark, setDark] as const;
}
