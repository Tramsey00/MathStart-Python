import { data } from 'react-router';
import { PageStatus } from '../../features/public-pages/page-status';

export const meta = () => [
  { title: 'Страница не найдена | MathStart' },
  { name: 'robots', content: 'noindex, nofollow' },
];

// Vite serves direct requests; the release build exports the shared error
// document, and FastAPI supplies its HTTP status at the requested address.
export function loader() {
  return import.meta.env.DEV ? data(null, { status: 404 }) : null;
}
export function clientLoader() { return null; }

export default function NotFound() {
  return <PageStatus missing />;
}
