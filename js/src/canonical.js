// Canonical form and hashing, matching src/lemmata/canonical.py byte for byte.

const MASK = "\u0000";

export function stripLeadingEquals(text) {
  const s = text.trim();
  return s.startsWith("=") ? s.slice(1) : s;
}

/** Same length as `s`; the inside of every string literal replaced by MASK. */
export function maskStrings(s) {
  const out = s.split("");
  let i = 0;
  const n = s.length;
  while (i < n) {
    if (s[i] === '"') {
      let j = i + 1;
      while (j < n) {
        if (s[j] === '"') {
          if (j + 1 < n && s[j + 1] === '"') { j += 2; continue; }
          break;
        }
        j++;
      }
      for (let k = i + 1; k < Math.min(j, n); k++) out[k] = MASK;
      i = j + 1;
    } else {
      i++;
    }
  }
  return out.join("");
}

export function canonicalFormula(text) {
  const s = stripLeadingEquals(text);
  const masked = maskStrings(s);
  let out = "";
  for (let i = 0; i < s.length; i++) {
    const ch = s[i];
    if (masked[i] === MASK || ch === '"') out += ch;
    else if (/\s/.test(ch)) continue;
    else out += ch.toUpperCase();
  }
  return out;
}

export async function sha256Hex(text) {
  const data = new TextEncoder().encode(text);
  const digest = await globalThis.crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, "0")).join("");
}

export async function formulaHash(text) {
  return sha256Hex(canonicalFormula(text));
}

/** Spans [start, end) of each top-level argument of the call whose "(" is at openIdx. */
export function splitArgs(masked, openIdx) {
  if (masked[openIdx] !== "(") throw new Error("openIdx must point at '('");
  let depth = 0;
  const spans = [];
  let start = openIdx + 1;
  for (let i = openIdx; i < masked.length; i++) {
    const ch = masked[i];
    if (ch === "(") depth++;
    else if (ch === ")") {
      depth--;
      if (depth === 0) { spans.push([start, i]); return spans; }
    } else if (ch === "," && depth === 1) {
      spans.push([start, i]);
      start = i + 1;
    }
  }
  throw new Error("unbalanced parentheses");
}
