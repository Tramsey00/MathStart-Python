import {describe,it,expect} from 'vitest';
import {safeReturn} from '../src/features/identity/session';
describe('MS-T009 safe internal return',()=>{
 it('rejects external, ambiguous and auth loops',()=>{
  for(const value of ['https://evil.test','//evil.test','/\\evil.test','/%2f%2fevil.test','/%255cauth','/auth?mode=login','/%61uth','/a\n','/auth/'])expect(safeReturn(value)).toBe('/account/');
 });
 it('keeps valid internal paths, queries and fragments',()=>{
  expect(safeReturn('/materials?grade=5-klass#topics')).toBe('/materials?grade=5-klass#topics');
 });
});
