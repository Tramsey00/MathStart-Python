import professional from './themes/professional.css?inline';
import exploremiam from './theme.css?inline';
import qrafthive from './themes/qrafthive.css?inline';

const palettes = { professional, exploremiam, qrafthive };
const names = { professional: 'Professional', exploremiam: 'ExploreMiam', qrafthive: 'QraftHive 1.0' };
const query = new URLSearchParams(location.search);
const requested = query.get('theme');
export const palette = requested && Object.hasOwn(palettes, requested) ? requested as keyof typeof palettes : 'qrafthive';
export const initialDark = query.get('mode') === 'dark';
const style = document.createElement('style');
style.id = 'selected-palette';
style.textContent = palettes[palette];
document.head.append(style);
document.documentElement.dataset.palette = palette;
document.documentElement.dataset.theme = initialDark ? 'dark' : 'light';
document.title = `MathStart · ${names[palette]}`;
