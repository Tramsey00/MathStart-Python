import { Outlet } from "react-router";
export const handle={boundary:"public"};
// I02 owns public loaders, metadata and selective SSG.
export default function PublicLayout(){return <Outlet/>;}
