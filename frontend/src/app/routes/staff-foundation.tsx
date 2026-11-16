import {Navigate,useLocation} from 'react-router';
import StaffWritePage from './staff-write';
import {staffResources,useStaffCapabilities} from '../../shared/ui/staff-workspace';
export {staffResources};
export const meta=()=>[{title:'Администрирование · MathStart'},{name:'robots',content:'noindex, nofollow'}];
export const handle={skipLink:{target:'staff-main',label:'К администрированию'}};
export default function StaffPage(){
 const {pathname}=useLocation(),hints=useStaffCapabilities();
 if(pathname==='/admin/'){
  const first=staffResources.find(r=>Object.values(hints.resources[r[0]]).some(Boolean));
  return first?<Navigate replace to={'/admin/'+first[1]+'/'}/>:null;
 }
 return <StaffWritePage/>;
}
