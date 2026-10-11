// @vitest-environment node
import { afterAll, beforeAll, expect, it } from "vitest";
import { mkdir, mkdtemp, writeFile, rm } from "node:fs/promises";
import { resolve, sep } from "node:path";
import type { AddressInfo } from "node:net";
import { createPreviewServer } from "../scripts/preview.mjs";

let directory: string;
const server = createPreviewServer;
let instance: ReturnType<typeof server>;
let base: string;
beforeAll(async () => {
  await mkdir(".cache", {recursive:true});
  directory = await mkdtemp(resolve(".cache/preview-test-"));
  await mkdir(directory + "/assets");
  await writeFile(directory + "/index.html", "<!doctype html><title>Anonymous shell</title>");
  await writeFile(directory + "/assets/sample.js", "export {};");
  instance = server(directory);
  await new Promise<void>(done => instance.listen(0,"127.0.0.1",done));
  base = "http://127.0.0.1:" + (instance.address() as AddressInfo).port;
});
afterAll(async () => {
  instance?.closeAllConnections();
  if (instance) await new Promise<void>((done,reject) => instance.close(error=>error?reject(error):done()));
  if (directory && directory.startsWith(resolve(".cache") + sep)) await rm(directory,{recursive:true});
});

it("serves only explicit foundation routes and existing generated assets", async () => {
  const home=await fetch(base + "/");
  expect(home.status).toBe(200);
  expect(home.headers.get("cache-control")).toBe("no-store");
  expect(await home.text()).toContain("Anonymous shell");
  const asset=await fetch(base + "/assets/sample.js");
  expect(asset.status).toBe(200);
  expect(asset.headers.get("content-type")).toContain("javascript");
});

it("does not apply a wildcard200 fallback to unknown/debug/API/missing assets", async () => {
  for (const path of ["/unknown/", "/__ui__/foundation/", "/__i01_reference__/shell/", "/api/v1/users/me/", "/assets/missing.js", "/assets/%2e%2e%2fpackage.json"]) {
    expect((await fetch(base + path)).status,path).toBe(404);
  }
});

it("never accepts mutations and preserves the account GET-only foundation", async () => {
  expect((await fetch(base + "/account/",{method:"HEAD"})).status).toBe(405);
  expect((await fetch(base + "/",{method:"POST"})).status).toBe(405);
  expect((await fetch(base + "/",{method:"HEAD"})).status).toBe(200);
});
