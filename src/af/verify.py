"""Check which modules a workbook carries and whether they match the registry."""

from __future__ import annotations

from pathlib import Path

from .canonical import formula_hash
from .registry import Registry
from .xlsx import from_file_formula, parse_label, read_defined_names

OK_STATUSES = {"current"}


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
            if label and registry.by_module_hash(label["hash"]):
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
    return {
        "file": str(path),
        "ok": all(e["status"] in OK_STATUSES for e in entries),
        "count": len(entries),
        "names": entries,
    }


def format_report(report: dict) -> str:
    lines = [f"{report['file']}: {report['count']} module name(s), {'ok' if report['ok'] else 'PROBLEMS'}"]
    for e in report["names"]:
        lines.append(f"  {e['status']:15s} {e['name']:24s} {e['message']}")
    return "\n".join(lines)
