import { useEffect, useState } from 'react';

export function useSiteTheme() {
  // The first client render must agree with SSG, independent of browser storage.
  const [dark, setDark] = useState(false);
  const [ready, setReady] = useState(false);
  useEffect(() => {
    try { setDark(localStorage.getItem('mathstart-mode') === 'dark'); } catch { /* Storage is optional. */ }
    setReady(true);
  }, []);
  useEffect(() => {
    if (!ready) return;
    document.documentElement.dataset.theme = dark ? 'dark' : 'light';
    try { localStorage.setItem('mathstart-mode', dark ? 'dark' : 'light'); } catch { /* Storage is optional. */ }
  }, [dark, ready]);
  return [dark, setDark] as const;
}
