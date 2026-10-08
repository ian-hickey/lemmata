// Read a published registry (index.json) and verify a workbook against it.

import { formulaHash } from "./canonical.js";
import { fromFileFormula, parseLabel, readDefinedNames } from "./xlsx.js";

export const DEFAULT_REGISTRY_URL = "https://ian-hickey.github.io/lemmata/";

export async function fetchIndex(url = DEFAULT_REGISTRY_URL, fetchImpl = globalThis.fetch) {
  const res = await fetchImpl(url.replace(/\/?$/, "/") + "index.json");
  if (!res.ok) throw new Error(`registry returned ${res.status}`);
  return res.json();
}

export function findModule(index, key) {
  const k = key.trim().toLowerCase();
  return index.modules.find((m) => m.id === k || m.name.toLowerCase() === k
    || (k.length >= 8 && (m.module_hash.startsWith(k) || m.formula_hash.startsWith(k)))) || null;
}

/** Modules plus their dependencies, dependencies first. */
export function withDependencies(index, modules) {
  const ordered = [];
  const seen = new Set();
  const visit = (m) => {
    if (seen.has(m.id)) return;
    for (const dep of m.dependencies || []) {
      const target = index.modules.find((x) => x.module_hash === dep.module_hash) || findModule(index, dep.id);
      if (!target) throw new Error(`${m.id} depends on ${dep.id}, which is not in the registry`);
      visit(target);
    }
    seen.add(m.id);
    ordered.push(m);
  };
  modules.forEach(visit);
  return ordered;
}

/** Same statuses as the Python verifier: current, unlabeled, label_mismatch, modified, unknown, advisory. */
export async function verifyWorkbook(xlsxBytes, index) {
  const prefix = (index.prefix || "LEMMA.").toUpperCase();
  const names = readDefinedNames(xlsxBytes);
  const entries = [];
  for (const name of Object.keys(names).sort()) {
    if (!name.toUpperCase().startsWith(prefix)) continue;
    const { formula, comment } = names[name];
    const fh = await formulaHash(fromFileFormula(formula));
    const label = parseLabel(comment);
    const matched = index.modules.find((m) => m.formula_hash === fh) || null;
    const entry = { name, formula_hash: fh, label: comment, module_id: matched?.id ?? label?.id ?? null, version: matched?.version ?? label?.version ?? null };
    if (!matched) {
      if (label && index.modules.some((m) => m.module_hash === label.hash)) {
        entry.status = "modified"; entry.message = `label claims ${label.id}@${label.version} but the formula text differs`;
      } else {
        entry.status = "unknown"; entry.message = "formula does not match any registry module";
      }
    } else {
      const advisories = (index.advisories || []).filter((a) => a.module_hash === matched.module_hash);
      if (advisories.length) {
        entry.status = "advisory"; entry.message = advisories.map((a) => `${a.id}: ${a.summary || ""}`).join("; "); entry.advisories = advisories;
      } else if (!label) {
        entry.status = "unlabeled"; entry.message = `matches ${matched.id}@${matched.version} but carries no label`;
      } else if (label.hash !== matched.module_hash) {
        entry.status = "label_mismatch"; entry.message = `formula is ${matched.id}@${matched.version}, label says ${label.id}@${label.version}`;
      } else {
        entry.status = "current"; entry.message = `${matched.id}@${matched.version}`;
      }
    }
    entries.push(entry);
  }
  return { ok: entries.every((e) => e.status === "current"), count: entries.length, names: entries };
}
