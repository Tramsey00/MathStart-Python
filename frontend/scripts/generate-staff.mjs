// Frozen staff contract projection for browser validation. Numeric int64 limits
// retain their exact decimal source bytes as internal schema constants.
import {readFileSync,writeFileSync} from 'node:fs';
const source=new URL('../../specs/migration/r02-v1/delivery-v1.schema.json',import.meta.url);
const api=new URL('../../specs/migration/r02-v1/delivery-staff-v1.openapi.json',import.meta.url);
const schema=JSON.parse(readFileSync(source,'utf8').replaceAll('9223372036854775807','"int64:9223372036854775807"'));
const operations=[];
for(const [path,item]of Object.entries(JSON.parse(readFileSync(api,'utf8')).paths))for(const[method,op]of Object.entries(item))if(['get','post','put','patch','delete'].includes(method))operations.push({path,method:method.toUpperCase(),...op});
const dto=JSON.parse(readFileSync(new URL('../../specs/api/schemas/dto-v1.schema.json',import.meta.url),'utf8'));
const errors={};
function collect(name){if(errors[name])return;errors[name]=dto.$defs[name];if(!errors[name])throw Error('Unknown error schema '+name);JSON.stringify(errors[name],(key,value)=>{if(key==='$ref')collect(value.split('/').at(-1));return value;});}
for(const op of operations)for(const [status,response]of Object.entries(op.responses))if(Number(status)>=400)collect(response.content['application/json'].schema.$ref.split('/').at(-1));
const raw=JSON.stringify({schema,errors,operations})+'\n';
const output=new URL('../src/shared/api/generated/staff-contracts.json',import.meta.url);
if(process.argv.includes('--check')){if(readFileSync(output,'utf8')!==raw)throw Error('Stale generated staff contracts');}
else writeFileSync(output,raw);
console.log('PASS: frozen staff contracts, '+operations.length+' methods');
