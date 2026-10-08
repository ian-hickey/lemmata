"""Check which modules a workbook carries and whether they match the registry."""

from __future__ import annotations

from pathlib import Path

import re

from .canonical import formula_hash, mask_strings, split_args
from .registry import Registry
from .xlsx import from_file_formula, parse_label, read_defined_names

OK_STATUSES = {"current", "outdated"}


def find_uses(path: Path | str, prefix: str) -> list[dict]:
    """Every cell formula that calls a prefixed name, with the argument text it passes."""
    import openpyxl

    call_re = re.compile(r"(?i)(?<![A-Za-z0-9_.])(" + re.escape(prefix) + r"[A-Za-z0-9_.]*)\(")
    wb = openpyxl.load_workbook(path)
    uses = []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                text = cell.value
                if not isinstance(text, str) or not text.startswith("="):
                    continue
                masked = mask_strings(text)
                for m in call_re.finditer(masked):
                    try:
                        spans = split_args(masked, m.end() - 1)
                        args = [text[a:b].strip() for a, b in spans]
                    except ValueError:
                        args = []
                    uses.append({"sheet": ws.title, "cell": cell.coordinate, "name": m.group(1).upper(), "arguments": args, "formula": text})
    return uses


def verify_workbook(path: Path | str, registry: Registry) -> dict:
    path = Path(path)
    names = read_defined_names(path)
    entries = []
    for name, (stored, comment) in sorted(names.items()):
        if not name.upper().startswith(registry.prefix.upper()):
            continue
        formula = from_file_formula(stored)
        fh = formula_hash(formula)
        label = parse_label(comment)
        matched = registry.by_formula_hash(fh)
        entry = {
            "name": name,
            "formula_hash": fh,
            "label": comment,
            "module_id": matched.id if matched else (label["id"] if label else None),
            "version": matched.version if matched else (label["version"] if label else None),
        }
        if matched is None:
            old = registry.historical_by_formula_hash(fh)
            if old is not None:
                advisories = registry.advisories_for(old["module_hash"])
                current = next((m for m in registry.modules if m.id == old["id"]), None)
                entry["module_id"], entry["version"] = old["id"], old["version"]
                latest = f"; current version is {current.version}" if current else ""
                if advisories:
                    entry["status"] = "advisory"
                    entry["message"] = "; ".join(f"{a['id']}: {a.get('summary', '')}" for a in advisories) + latest
                    entry["advisories"] = advisories
                else:
                    entry["status"] = "outdated"
                    entry["message"] = f"{old['id']}@{old['version']} was published and later superseded{latest}"
            elif label and (registry.by_module_hash(label["hash"]) or any(e.get("module_hash") == label["hash"] for e in registry.history)):
                entry["status"] = "modified"
                entry["message"] = f"label claims {label['id']}@{label['version']} but the formula text differs"
            else:
                entry["status"] = "unknown"
                entry["message"] = "formula does not match any registry module"
        else:
            advisories = registry.advisories_for(matched.module_hash)
            if advisories:
                entry["status"] = "advisory"
                entry["message"] = "; ".join(f"{a['id']}: {a.get('summary', '')}" for a in advisories)
                entry["advisories"] = advisories
            elif label is None:
                entry["status"] = "unlabeled"
                entry["message"] = f"matches {matched.id}@{matched.version} but carries no label"
            elif label["hash"] != matched.module_hash:
                entry["status"] = "label_mismatch"
                entry["message"] = f"formula is {matched.id}@{matched.version}, label says {label['id']}@{label['version']}"
            else:
                entry["status"] = "current"
                entry["message"] = f"{matched.id}@{matched.version}"
        entries.append(entry)
    uses = find_uses(path, registry.prefix)
    defined = {e["name"].upper() for e in entries}
    for e in entries:
        e["uses"] = [u for u in uses if u["name"] == e["name"].upper()]
    undefined = sorted({u["name"] for u in uses if u["name"] not in defined})
    return {
        "file": str(path),
        "ok": all(e["status"] in OK_STATUSES for e in entries) and not undefined,
        "count": len(entries),
        "names": entries,
        "undefined": undefined,
        "uses": uses,
    }


def format_report(report: dict) -> str:
    lines = [f"{report['file']}: {report['count']} module name(s), {'ok' if report['ok'] else 'PROBLEMS'}"]
    for e in report["names"]:
        lines.append(f"  {e['status']:15s} {e['name']:24s} {e['message']}  (used in {len(e.get('uses', []))} cell(s))")
        for u in e.get("uses", []):
            lines.append(f"      {u['sheet']}!{u['cell']}: {u['name']}({', '.join(u['arguments'])})")
    for name in report.get("undefined", []):
        lines.append(f"  {'undefined':15s} {name:24s} called by a cell but not defined in the workbook")
    return "\n".join(lines)
