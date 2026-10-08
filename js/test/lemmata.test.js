import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { execFileSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  canonicalFormula, formulaHash, toFileFormula, fromFileFormula, declaredNames,
  readDefinedNames, injectModules, createWorkbook, verifyWorkbook, withDependencies, findModule,
} from "../src/index.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, "..", "..");

/** The registry index built from this checkout by the Python tooling, so both sides are compared. */
function localIndex() {
  const out = execFileSync("uv", ["run", "lemma", "list", "--json"], { cwd: repo, encoding: "utf8" });
  return { prefix: "LEMMA.", modules: JSON.parse(out), advisories: [] };
}

test("canonical form matches the Python rule", () => {
  assert.equal(canonicalFormula("=LAMBDA(x, y,\n  if(x > y, \"a  b\", y))"), 'LAMBDA(X,Y,IF(X>Y,"a  b",Y))');
});

test("prefixes are added, idempotent, and reversible", () => {
  const f = "LAMBDA(s, e, IF(s > e, #VALUE!, LET(n, 2, SEQUENCE(n) + e)))";
  const once = toFileFormula(f);
  assert.equal(once, "_xlfn.LAMBDA(_xlpm.s, _xlpm.e, IF(_xlpm.s > _xlpm.e, #VALUE!, _xlfn.LET(_xlpm.n, 2, _xlfn.SEQUENCE(_xlpm.n) + _xlpm.e)))");
  assert.equal(toFileFormula(once), once);
  assert.equal(fromFileFormula(once), f);
  assert.deepEqual([...declaredNames(f)].sort(), ["e", "n", "s"]);
});

test("hashes agree with the Python registry for every module", async () => {
  const index = localIndex();
  for (const m of index.modules) {
    assert.equal(await formulaHash(m.formula), m.formula_hash, m.id);
    assert.equal(toFileFormula(m.formula), m.formula_xlsx, m.id);
  }
});

test("inject into a new workbook, read back, and verify", async () => {
  const index = localIndex();
  const mods = withDependencies(index, [findModule(index, "cagr"), findModule(index, "LEMMA.NPV")]);
  const bytes = injectModules(createWorkbook(), mods);
  const names = readDefinedNames(bytes);
  assert.deepEqual(Object.keys(names).sort(), ["LEMMA.CAGR", "LEMMA.NPV"]);
  assert.match(names["LEMMA.CAGR"].formula, /^_xlfn\.LAMBDA\(_xlpm\.start_value/);
  const report = await verifyWorkbook(bytes, index);
  assert.equal(report.ok, true);
  assert.deepEqual(report.names.map((e) => e.status), ["current", "current"]);

  // Re-injecting replaces rather than duplicates.
  const again = readDefinedNames(injectModules(bytes, mods));
  assert.equal(Object.keys(again).length, 2);
});

test("a hand-edited formula is reported as modified", async () => {
  const index = localIndex();
  const bytes = injectModules(createWorkbook(), [findModule(index, "cagr")]);
  const tampered = { ...findModule(index, "cagr"), formula: findModule(index, "cagr").formula.replace("- 1", "- 2") };
  const edited = injectModules(bytes, [tampered]);
  const report = await verifyWorkbook(edited, index);
  assert.equal(report.names[0].status, "modified");
});

test("reads names from a workbook the Python injector wrote", async () => {
  const file = path.join(repo, "examples", "phase0.xlsx");
  if (!existsSync(file)) return;
  const report = await verifyWorkbook(readFileSync(file), localIndex());
  assert.equal(report.ok, true);
  assert.equal(report.count, 3);
});
