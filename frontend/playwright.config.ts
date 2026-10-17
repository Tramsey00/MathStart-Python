import {defineConfig} from '@playwright/test';
import {resolve} from 'node:path';
process.env.PLAYWRIGHT_BROWSERS_PATH ||= resolve('.cache/browsers');
const projects=[{name:'chrome',browserName:'chromium' as const,channel:'chrome'},{name:'edge',browserName:'chromium' as const,channel:'msedge'},{name:'firefox',browserName:'firefox' as const}];
export default defineConfig({
 testDir:'./e2e',fullyParallel:false,workers:2,retries:0,timeout:60_000,
 testIgnore:process.env.MATHSTART_E2E_SCOPE==='i02'?[]:['**/i02.spec.ts'],
 reporter:[['list'],['json']],outputDir:'test-results',
 use:{baseURL:process.env.MATHSTART_E2E_BASE_URL || 'http://127.0.0.1:8131',trace:'retain-on-failure',screenshot:'only-on-failure'},
 projects:projects.flatMap(p=>[360,768,1440].map(width=>({name:p.name+'-'+width,use:{browserName:p.browserName,...('channel' in p?{channel:p.channel}:{}),viewport:{width,height:width===360?800:width===768?1024:1000}}}))),
});
