import {SiteShell} from './site-shell';
// Existing root error presentation, shared without changing its policy or design.
export function RouteErrorPage({missing}:{missing:boolean}){
 return <SiteShell><main id="main-content" tabIndex={-1}><h1>{missing ? "Страница не найдена" : "Не удалось открыть страницу"}</h1></main></SiteShell>;
}
