// JSON-only boundary: reject accessors, non-finite numbers, cycles and coercion.
export function isJsonTree(value: unknown): boolean {
  const seen = new Set<object>(); let nodes = 0;
  function visit(v: unknown, depth: number): boolean {
    if (++nodes > 100000 || depth > 64) return false;
    if (v === null || typeof v === "string" || typeof v === "boolean") return true;
    if (typeof v === "number") return Number.isFinite(v);
    if (typeof v !== "object" || seen.has(v)) return false;
    const proto = Object.getPrototypeOf(v);
    if (!Array.isArray(v) && proto !== Object.prototype && proto !== null) return false;
    seen.add(v);
    const descriptors = Object.getOwnPropertyDescriptors(v);
    if (Reflect.ownKeys(v).some(k => typeof k !== "string")) return false;
    if (Array.isArray(v)) {
      if (Object.keys(descriptors).length !== v.length + 1) return false;
      for (let i=0; i<v.length; i++) if (!Object.hasOwn(descriptors,String(i))) return false;
    }
    for (const [key,d] of Object.entries(descriptors)) {
      if (Array.isArray(v) && key === "length") continue;
      if (!("value" in d) || !d.enumerable || !visit(d.value,depth+1)) return false;
    }
    seen.delete(v); return true;
  }
  try { return visit(value,0); } catch { return false; }
}

// Preserve JSON semantics while rejecting duplicate members (JSON.parse alone loses them).
export function parseJson(text: string): unknown {
  let pos=0;
  const fail=(): never => { throw new Error("Invalid JSON"); };
  const space=() => { while (/[ \t\r\n]/.test(text[pos] ?? "") && pos<text.length) pos++; };
  function string(): string {
    const start=pos++;
    while (pos<text.length) {
      const c=text[pos++];
      if (c === "\\") { pos++; continue; }
      if (c === '"') return JSON.parse(text.slice(start,pos)) as string;
    }
    return fail();
  }
  function value(depth: number): unknown {
    if (depth>64) return fail(); space();
    const c=text[pos];
    if (c === '"') return string();
    if (c === "{" || c === "[") {
      pos++; space();
      const object=c === "{"; const out: Record<string,unknown>=Object.create(null) as Record<string,unknown>;
      const list: unknown[]=[]; const close=object?"}":"]";
      if (text[pos]===close) {pos++;return object?out:list;}
      for (;;) {
        space(); let key="";
        if (object) {
          if (text[pos]!=='"') return fail(); key=string(); space();
          if (Object.hasOwn(out,key) || text[pos++]!==":") return fail();
        }
        const child=value(depth+1); if (object) out[key]=child; else list.push(child);
        space(); const next=text[pos++]; if (next===close) return object?out:list;
        if (next!==",") return fail();
      }
    }
    for (const [token,result] of [["true",true],["false",false],["null",null]] as const) {
      if (text.startsWith(token,pos)) {pos+=token.length;return result;}
    }
    const number=text.slice(pos).match(/^-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?/);
    if (!number) return fail();
    pos+=number[0].length; const n=Number(number[0]); return Number.isFinite(n)?n:fail();
  }
  const out=value(0); space(); if(pos!==text.length) fail(); return out;
}
