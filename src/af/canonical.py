"""Formula text utilities: canonical form, hashing, and light parsing.

Nothing here understands Excel semantics. It only tracks string literals and
parentheses well enough to normalize text and find argument boundaries.
"""

from __future__ import annotations

import hashlib
import json
import re

MASK = "\x00"
IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
CALL_RE = re.compile(r"(?<![A-Za-z0-9_.])([A-Za-z_][A-Za-z0-9_.]*)\(")


def strip_leading_equals(text: str) -> str:
    s = text.strip()
    return s[1:] if s.startswith("=") else s


def mask_strings(s: str) -> str:
    """Return s with the inside of every string literal replaced by MASK.

    The result has the same length as s, so indices found on the mask apply
    to the original. Quotes themselves are kept. A doubled quote inside a
    literal is an escaped quote.
    """
    out = list(s)
    i, n = 0, len(s)
    while i < n:
        if s[i] == '"':
            j = i + 1
            while j < n:
                if s[j] == '"':
                    if j + 1 < n and s[j + 1] == '"':
                        j += 2
                        continue
                    break
                j += 1
            for k in range(i + 1, min(j, n)):
                out[k] = MASK
            i = j + 1
        else:
            i += 1
    return "".join(out)


def canonical_formula(text: str) -> str:
    """Whitespace removed and upper-cased outside string literals, no leading '='."""
    s = strip_leading_equals(text)
    masked = mask_strings(s)
    out = []
    for ch, m in zip(s, masked):
        if m == MASK or ch == '"':
            out.append(ch)
        elif ch.isspace():
            continue
        else:
            out.append(ch.upper())
    return "".join(out)


def canonical_metadata(meta: dict) -> str:
    return json.dumps(meta, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def formula_hash(text: str) -> str:
    return hashlib.sha256(canonical_formula(text).encode("utf-8")).hexdigest()


def module_hash(formula_text: str, meta: dict) -> str:
    payload = canonical_formula(formula_text) + "\n" + canonical_metadata(meta)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def split_args(masked: str, open_idx: int) -> list[tuple[int, int]]:
    """Spans of each top-level argument of the call whose '(' sits at open_idx."""
    if masked[open_idx] != "(":
        raise ValueError("open_idx must point at '('")
    depth = 0
    spans: list[tuple[int, int]] = []
    start = open_idx + 1
    for i in range(open_idx, len(masked)):
        ch = masked[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                spans.append((start, i))
                return spans
        elif ch == "," and depth == 1:
            spans.append((start, i))
            start = i + 1
    raise ValueError("unbalanced parentheses")


def lambda_parameters(formula: str) -> list[str]:
    """Parameter names of the outermost LAMBDA, in order."""
    s = strip_leading_equals(formula)
    masked = mask_strings(s)
    idx = masked.find("(")
    head = masked[:idx].strip().upper() if idx >= 0 else ""
    if head not in ("LAMBDA", "_XLFN.LAMBDA"):
        raise ValueError("formula does not start with LAMBDA(")
    spans = split_args(masked, idx)
    return [s[a:b].strip() for a, b in spans[:-1]]


def function_calls(formula: str) -> set[str]:
    """Upper-cased names of every function called anywhere in the formula."""
    masked = mask_strings(strip_leading_equals(formula))
    return {m.group(1).upper() for m in CALL_RE.finditer(masked)}
