import {StaffWorkspace} from "../../shared/ui/staff-workspace";
import { Navigate, Outlet, useLocation } from "react-router";
export const handle={boundary:"staff",private:true};
export const meta=()=>[{name:"robots",content:"noindex, nofollow"}];
// This is a route boundary, not a permission gate. The server owns authorization.
export default function StaffLayout(){const {pathname}=useLocation();if(pathname.startsWith("/admin/password_change/"))return <Navigate replace to="/account/?section=security"/>;return <StaffWorkspace><Outlet/></StaffWorkspace>;}

export function ErrorBoundary(){return <StaffWorkspace><main id="staff-main" className="staff-main" tabIndex={-1}><h1>Не удалось открыть раздел</h1><p>Обновите страницу или вернитесь к списку разделов.</p><a href="/admin/">Администрирование</a></main></StaffWorkspace>;}
