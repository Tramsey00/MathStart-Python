import { Outlet } from "react-router";
export const handle={boundary:"staff",private:true};
export const meta=()=>[{name:"robots",content:"noindex, nofollow"}];
// This is a route boundary, not a permission gate. The server owns authorization.
export default function StaffLayout(){return <Outlet/>;}
