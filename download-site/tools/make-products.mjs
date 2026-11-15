// ダウンロードページ用の products.json を作るスクリプト
//
// 使い方:
//   1. tools/products.source.json に商品名・ダウンロードコード・ファイルのURLを書く
//   2. node tools/make-products.mjs を実行する
//   3. できた products.json を公開する（products.source.json は公開しない）
//
// ファイルのURLは、ダウンロードコードを鍵にして暗号化されます。
// ページのソースを見ても、コードを知らない人にはURLがわかりません。

import { readFile, writeFile } from "node:fs/promises";
import { webcrypto as crypto } from "node:crypto";
import { fileURLToPath } from "node:url";
import path from "node:path";

const here = path.dirname(fileURLToPath(import.meta.url));
const srcPath = path.join(here, "products.source.json");
// まだ無ければ products.source.example.json をコピーして作ってください
const outPath = path.join(here, "..", "products.json");
const ITERATIONS = 200000;

const b64 = (buf) => Buffer.from(buf).toString("base64");
export const normalize = (code) => code.trim().toUpperCase().replace(/\s+/g, "");

async function encrypt(code, payload) {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const base = await crypto.subtle.importKey("raw", new TextEncoder().encode(normalize(code)), "PBKDF2", false, ["deriveKey"]);
  const key = await crypto.subtle.deriveKey(
    { name: "PBKDF2", salt, iterations: ITERATIONS, hash: "SHA-256" },
    base, { name: "AES-GCM", length: 256 }, false, ["encrypt"]
  );
  const data = await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, new TextEncoder().encode(JSON.stringify(payload)));
  return { salt: b64(salt), iv: b64(iv), data: b64(data), iterations: ITERATIONS };
}

const source = JSON.parse(await readFile(srcPath, "utf8"));
const products = [];
for (const p of source.products) {
  if (!p.code || !Array.isArray(p.files) || p.files.length === 0) {
    throw new Error(`「${p.name}」にダウンロードコードかファイルがありません`);
  }
  products.push({
    id: p.id,
    name: p.name,
    category: p.category,
    summary: p.summary,
    updated: p.updated,
    locked: await encrypt(p.code, { files: p.files, note: p.note ?? "" }),
  });
}
await writeFile(outPath, JSON.stringify({ shop: source.shop, products }, null, 2) + "\n");
console.log(`${products.length}件の商品を ${path.relative(process.cwd(), outPath)} に書き出しました`);
