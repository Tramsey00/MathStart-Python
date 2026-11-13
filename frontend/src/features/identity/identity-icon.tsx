type IconName = 'user' | 'lock' | 'book' | 'shield' | 'logout' | 'arrow';

// Small interface icons, using the same round line treatment as the site chrome.
export function IdentityIcon({name}: {name: IconName}) {
  return <svg className="identity-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    {name === 'user' && <><circle cx="12" cy="8" r="4"/><path d="M4 21v-2a8 8 0 0 1 16 0v2"/></>}
    {name === 'lock' && <><rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/><path d="M12 14v3"/></>}
    {name === 'book' && <><path d="M12 5v16M3 3h5a4 4 0 0 1 4 2 4 4 0 0 1 4-2h5v16h-5a4 4 0 0 0-4 2 4 4 0 0 0-4-2H3Z"/></>}
    {name === 'shield' && <><path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6Z"/><path d="m9 12 2 2 4-4"/></>}
    {name === 'logout' && <><path d="M10 4H5v16h5m3-12 4 4-4 4m-5-4h13"/></>}
    {name === 'arrow' && <path d="M4 12h16m-6-6 6 6-6 6"/>}
  </svg>;
}
