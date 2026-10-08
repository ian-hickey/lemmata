// Translate formulas to and from the .xlsx file format, and read or write
// defined names in a workbook. Matches src/lemmata/xlsx.py.

import { unzipSync, zipSync, strToU8, strFromU8 } from "fflate";
import FUTURE_FUNCTIONS from "./future-functions.json" with { type: "json" };
import { maskStrings, splitArgs, stripLeadingEquals } from "./canonical.js";

const IDENT_RE = /^[A-Za-z_][A-Za-z0-9_]*$/;
const CALL_RE = /(?<![A-Za-z0-9_.])(?:_xlfn\.)?(LAMBDA|LET)\(/gi;
const TOKEN_RE = /(?<![A-Za-z0-9_.#$])([A-Za-z_][A-Za-z0-9_.]*)(\()?/g;
const PREFIX_RE = /_xlfn\.|_xlpm\.|_xlws\./g;
const LABEL_RE = /^\s*([a-z][a-z0-9_]*)@(\d+\.\d+\.\d+) sha256:([0-9a-f]{64})\s*$/;

/** Lower-cased names declared as LAMBDA parameters or LET variables, at any depth. */
export function declaredNames(formula) {
  const s = stripLeadingEquals(formula);
  const masked = maskStrings(s);
  const names = new Set();
  for (const m of masked.matchAll(CALL_RE)) {
    const spans = splitArgs(masked, m.index + m[0].length - 1);
    const candidates = m[1].toUpperCase() === "LAMBDA"
      ? spans.slice(0, -1)
      : spans.slice(0, -1).filter((_, i) => i % 2 === 0);
    for (const [a, b] of candidates) {
      let tok = s.slice(a, b).trim();
      if (tok.toLowerCase().startsWith("_xlpm.")) tok = tok.slice(6);
      if (IDENT_RE.test(tok)) names.add(tok.toLowerCase());
    }
  }
  return names;
}

/** Add the _xlfn. and _xlpm. prefixes the file format requires. */
export function toFileFormula(formula) {
  const s = stripLeadingEquals(formula);
  const names = declaredNames(s);
  const masked = maskStrings(s);
  let out = "";
  let last = 0;
  for (const m of masked.matchAll(TOKEN_RE)) {
    const [, ident, isCall] = m;
    let replacement = null;
    if (isCall) {
      const stored = FUTURE_FUNCTIONS[ident.toUpperCase()];
      if (stored) replacement = stored + "(";
    } else if (names.has(ident.toLowerCase())) {
      replacement = "_xlpm." + ident;
    }
    if (replacement !== null) {
      out += s.slice(last, m.index) + replacement;
      last = m.index + m[0].length;
    }
  }
  return out + s.slice(last);
}

/** Remove the file-format prefixes outside string literals. */
export function fromFileFormula(text) {
  const s = stripLeadingEquals(text);
  const masked = maskStrings(s);
  let out = "";
  let last = 0;
  for (const m of masked.matchAll(PREFIX_RE)) {
    out += s.slice(last, m.index);
    last = m.index + m[0].length;
  }
  return out + s.slice(last);
}

export function parseLabel(comment) {
  if (!comment) return null;
  const m = LABEL_RE.exec(comment);
  return m ? { id: m[1], version: m[2], hash: m[3] } : null;
}

const escapeXml = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const unescapeXml = (s) => s.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&amp;/g, "&");

const DEFINED_NAME_RE = /<definedName\b([^>]*)>([\s\S]*?)<\/definedName>/g;
const attr = (attrs, name) => {
  const m = new RegExp(`\\b${name}="([^"]*)"`).exec(attrs);
  return m ? unescapeXml(m[1]) : null;
};

/** Workbook-scoped defined names as { name: { formula, comment } }. */
export function readDefinedNames(xlsxBytes) {
  const files = unzipSync(new Uint8Array(xlsxBytes));
  const xml = strFromU8(files["xl/workbook.xml"]);
  const names = {};
  for (const m of xml.matchAll(DEFINED_NAME_RE)) {
    const attrs = m[1];
    if (attr(attrs, "localSheetId") !== null) continue;
    const name = attr(attrs, "name");
    names[name] = { formula: unescapeXml(m[2]), comment: attr(attrs, "comment") };
  }
  return names;
}

/**
 * Write modules into the workbook as defined names and return the new bytes.
 * Each module is an index.json entry or get_module result: { name, formula, id, version, module_hash }.
 */
export function injectModules(xlsxBytes, modules) {
  const files = unzipSync(new Uint8Array(xlsxBytes));
  let xml = strFromU8(files["xl/workbook.xml"]);
  const wanted = new Map(modules.map((m) => [m.name.toUpperCase(), m]));

  // Drop any existing definition of the names we are writing.
  xml = xml.replace(DEFINED_NAME_RE, (whole, attrs) => {
    const name = attr(attrs, "name");
    return name && attr(attrs, "localSheetId") === null && wanted.has(name.toUpperCase()) ? "" : whole;
  });
  const entries = modules.map((m) => {
    const label = `${m.id}@${m.version} sha256:${m.module_hash}`;
    return `<definedName name="${escapeXml(m.name)}" comment="${escapeXml(label)}">${escapeXml(toFileFormula(m.formula))}</definedName>`;
  }).join("");

  if (/<definedNames\s*\/>/.test(xml)) {
    xml = xml.replace(/<definedNames\s*\/>/, `<definedNames>${entries}</definedNames>`);
  } else if (/<definedNames>/.test(xml)) {
    xml = xml.replace(/<\/definedNames>/, `${entries}</definedNames>`);
  } else {
    // Schema order: definedNames follows sheets (and functionGroups/externalReferences if present).
    const anchor = /<\/sheets>(?:\s*<functionGroups[\s\S]*?<\/functionGroups>)?(?:\s*<externalReferences[\s\S]*?<\/externalReferences>)?/;
    if (!anchor.test(xml)) throw new Error("xl/workbook.xml has no <sheets> element");
    xml = xml.replace(anchor, (m) => `${m}<definedNames>${entries}</definedNames>`);
  }
  files["xl/workbook.xml"] = strToU8(xml);
  return zipSync(files, { level: 6 });
}

const MINIMAL = {
  "[Content_Types].xml": `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>`,
  "_rels/.rels": `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>`,
  "xl/workbook.xml": `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets></workbook>`,
  "xl/_rels/workbook.xml.rels": `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>`,
  "xl/worksheets/sheet1.xml": `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData/></worksheet>`,
  // Readers such as IronCalc require a stylesheet part even when no styles are used.
  "xl/styles.xml": `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts><fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>`,
};

/** A minimal empty workbook to inject into when no file exists yet. */
export function createWorkbook() {
  const files = {};
  for (const [path, text] of Object.entries(MINIMAL)) files[path] = strToU8(text);
  return zipSync(files, { level: 6 });
}
