type Bundle=Record<string,{type:"chunk";modules:Record<string,unknown>}|{type:"asset"}>;
export function productionBoundaryPlugin():{name:string;apply:"build";generateBundle(options:unknown,bundle:Bundle):void};
