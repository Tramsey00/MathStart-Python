import {mkdirSync,writeFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
export function productionBoundaryPlugin() {
  return {name:"mathstart-production-boundary",apply:"build",
    generateBundle(_options,bundle) {
      const modules=[...new Set(Object.values(bundle).flatMap(chunk=>chunk.type==="chunk"?Object.keys(chunk.modules):[]))]
        .map(p=>p.replaceAll("\\","/")).sort();
      const forbidden=modules.filter(p=>/\/src\/debug\/|foundation-gallery|\/layouts\/debug\.tsx|\/specs\/.*fixtures\/|synthetic-.*\.json|UiFixturePack\.mjs|shell-reference\.mjs/.test(p));
      if(forbidden.length)throw new Error("Forbidden production modules: "+forbidden.join(", "));
      const path=fileURLToPath(new URL("../.cache/",import.meta.url));mkdirSync(path,{recursive:true});
      const target=modules.some(p=>p.includes("react-dom/client"))?"client":"server";
      writeFileSync(path+"production-"+target+"-modules.json",JSON.stringify({forbidden,modules},null,2)+"\n");
    }};
}
