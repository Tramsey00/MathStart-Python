// Retired staff UI paths use the existing root 404 boundary.
export function clientLoader(){throw new Response(null,{status:404});}
clientLoader.hydrate=true as const;
export default function UnavailableStaffPage(){return null;}
