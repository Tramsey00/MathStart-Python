import { Outlet } from "react-router";
export const handle={boundary:"account",private:true};
export const meta=()=>[{name:"robots",content:"noindex, nofollow"}];
// No loader/SSG/private data. I04 supplies session reconciliation and forms.
export default function AccountLayout(){return <Outlet/>;}
