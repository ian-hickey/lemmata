"""Build the static registry: index.json, llms.txt, and one folder per module hash."""

from __future__ import annotations

import gzip
import io
import json
import shutil
import tarfile
from datetime import datetime, timezone
from pathlib import Path

from .registry import Registry
from .xlsx import to_file_formula


def deterministic_tarball(folder: Path, dest: Path, arcname: str) -> None:
    """A .tar.gz whose bytes depend only on the folder's contents, so its digest is stable."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        for path in sorted(p for p in folder.rglob("*") if p.is_file()):
            info = tar.gettarinfo(path, arcname=f"{arcname}/{path.relative_to(folder).as_posix()}")
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            info.mtime = 0
            info.mode = 0o644
            with path.open("rb") as fh:
                tar.addfile(info, fh)
    with dest.open("wb") as fh:
        with gzip.GzipFile(fileobj=fh, mode="wb", mtime=0) as gz:
            gz.write(buf.getvalue())


def build_index(registry: Registry, out: Path | str) -> dict:
    out = Path(out)
    (out / "modules").mkdir(parents=True, exist_ok=True)
    entries = []
    for m in registry.modules:
        entry = m.to_index_entry()
        entries.append(entry)
        dest = out / "modules" / m.module_hash
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(m.path, dest)
        (dest / "formula.xlsx.txt").write_text(to_file_formula(m.formula) + "\n", encoding="utf-8")
        (dest / "hashes.json").write_text(
            json.dumps({"formula_hash": m.formula_hash, "module_hash": m.module_hash}, indent=2) + "\n",
            encoding="utf-8",
        )
        deterministic_tarball(dest, out / "modules" / f"{m.module_hash}.tar.gz", m.module_hash)
        entry["archive"] = f"modules/{m.module_hash}.tar.gz"
    index = {
        "spec": "0.1",
        "prefix": registry.prefix,
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "modules": entries,
        "advisories": registry.advisories,
    }
    (out / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Lemmata",
        "",
        "Reviewed, tested, hash-pinned spreadsheet formulas (Excel LAMBDA). Each module below is",
        "served at modules/<module_hash>/ with module.yaml, formula.lambda, tests.yaml, README.md,",
        "and formula.xlsx.txt (the formula as it must be stored in an .xlsx defined name).",
        "Run verify on any workbook before returning it: every LEMMA.* name must re-hash to a listed formula_hash.",
        "",
    ]
    for e in entries:
        params = ", ".join(p["name"] for p in e["parameters"])
        lines.append(f"- {e['name']}({params}) v{e['version']}: {e['summary']} [module_hash {e['module_hash']}]")
    (out / "llms.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return index
