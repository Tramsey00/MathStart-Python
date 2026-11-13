// MS-T009 extension to the canonical Identity transport, no independent fetch/auth.
type Ack={data:{completed:true};meta:{version:'http-v1';request_id:string}};
export interface AccountContracts {
 account_state:{request:never;response:{data:{email:string|null;email_verified:boolean;mail_available:boolean};meta:{version:'http-v1';request_id:string}}};
 account_email:{request:{current_password:string;email:string};response:Ack};
 account_password:{request:{current_password:string;new_password:string};response:Ack};
 account_sessions:{request:{current_password:string};response:Ack};
 account_recover:{request:{username:string};response:Ack};
 account_verify:{request:{token:string};response:Ack};
 account_reset:{request:{token:string;new_password:string};response:Ack};
}
const object=(v:unknown):v is Record<string,unknown>=>!!v&&typeof v==='object'&&!Array.isArray(v);
const fields=(keys:string[])=>(v:unknown)=>object(v)&&Object.keys(v).length===keys.length&&keys.every(k=>typeof v[k]==='string');
const ack=(v:unknown)=>object(v)&&object(v.data)&&v.data.completed===true&&object(v.meta)&&v.meta.version==='http-v1'&&typeof v.meta.request_id==='string';
const state=(v:unknown)=>object(v)&&object(v.data)&&(v.data.email===null||typeof v.data.email==='string')&&typeof v.data.email_verified==='boolean'&&typeof v.data.mail_available==='boolean'&&object(v.meta)&&v.meta.version==='http-v1';
import BadRequestError from './generated/BadRequestError.mjs';
import AuthenticationError from './generated/AuthenticationError.mjs';
import ForbiddenError from './generated/ForbiddenError.mjs';
import ConflictEnvelope from './generated/ConflictEnvelope.mjs';
import RateLimitError from './generated/RateLimitError.mjs';
import UnavailableError from './generated/UnavailableError.mjs';
function operation(action:string,keys:string[],read=false){return {path:`/api/v1/account/${action}/`,method:read?'GET':'POST',receipt:false as const,request:read?null:fields(keys),success:200,responses:{200:read?state:ack,400:BadRequestError,401:AuthenticationError,403:ForbiddenError,409:ConflictEnvelope,429:RateLimitError,503:UnavailableError}};}
export const accountOperations={
 account_state:operation('state',[],true),account_email:operation('email',['current_password','email']),
 account_password:operation('password',['current_password','new_password']),account_sessions:operation('sessions',['current_password']),
 account_recover:operation('recover',['username']),account_verify:operation('verify',['token']),account_reset:operation('reset',['token','new_password'])
};
