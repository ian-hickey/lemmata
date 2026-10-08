"""The lemma command: list, check, test, hash, show, add, verify, build-index."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .index import build_index
from .registry import Registry, RegistryError
from .runner import run_all
from .verify import format_report, verify_workbook
from .xlsx import inject


def cmd_list(args, reg: Registry) -> int:
    rows = [m.to_index_entry() for m in reg.modules]
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    for m in reg.modules:
        params = ", ".join(p["name"] for p in m.parameters)
        print(f"{m.name}({params})  v{m.version}  {m.module_hash[:12]}\n    {m.summary}")
    return 0


def cmd_check(args, reg: Registry) -> int:
    modules = [reg.get(i) for i in args.ids] if args.ids else reg.modules
    failed = 0
    for m in modules:
        problems = m.validate(reg.prefix)
        status = "ok" if not problems else "FAIL"
        print(f"{status:4s} {m.id}")
        for p in problems:
            print(f"     - {p}")
        failed += bool(problems)
    return 1 if failed else 0


def cmd_test(args, reg: Registry) -> int:
    results = run_all(reg, args.ids or None)
    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2, default=str))
    else:
        for r in results:
            mark = "pass" if r.passed else "FAIL"
            line = f"{mark} {r.module_id}: {r.case}"
            if not r.passed:
                line += f"\n     {r.message}"
            print(line)
        passed = sum(r.passed for r in results)
        print(f"{passed}/{len(results)} cases passed on {results[0].engine if results else 'no engine'}")
    return 0 if all(r.passed for r in results) else 1


def cmd_hash(args, reg: Registry) -> int:
    m = reg.get(args.id)
    print(json.dumps({"id": m.id, "version": m.version, "formula_hash": m.formula_hash, "module_hash": m.module_hash}, indent=2))
    return 0


def cmd_show(args, reg: Registry) -> int:
    m = reg.get(args.id)
    print((m.path / "module.yaml").read_text(encoding="utf-8").rstrip())
    print("\n# formula.lambda\n" + m.formula.rstrip())
    print(f"\n# formula_hash {m.formula_hash}\n# module_hash  {m.module_hash}")
    return 0


def cmd_add(args, reg: Registry) -> int:
    modules = reg.with_dependencies([reg.get(i) for i in args.ids])
    written = inject(args.workbook, modules, out=args.out)
    target = args.out or args.workbook
    for name in written:
        print(f"wrote {name}")
    print(f"saved {target}")
    return 0


def cmd_verify(args, reg: Registry) -> int:
    report = verify_workbook(args.workbook, reg)
    print(json.dumps(report, indent=2) if args.json else format_report(report))
    return 0 if report["ok"] else 1


def cmd_build_index(args, reg: Registry) -> int:
    index = build_index(reg, args.out)
    print(f"wrote {args.out}/index.json with {len(index['modules'])} module(s)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="lemma", description="Lemmata registry tools")
    p.add_argument("--registry", help="path to a registry checkout (default: this package's repo)")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("list", help="list modules"); s.add_argument("--json", action="store_true"); s.set_defaults(fn=cmd_list)
    s = sub.add_parser("check", help="validate modules against the spec"); s.add_argument("ids", nargs="*"); s.set_defaults(fn=cmd_check)
    s = sub.add_parser("test", help="run module tests on IronCalc"); s.add_argument("ids", nargs="*"); s.add_argument("--json", action="store_true"); s.set_defaults(fn=cmd_test)
    s = sub.add_parser("hash", help="print a module's hashes"); s.add_argument("id"); s.set_defaults(fn=cmd_hash)
    s = sub.add_parser("show", help="print a module's metadata and formula"); s.add_argument("id"); s.set_defaults(fn=cmd_show)
    s = sub.add_parser("add", help="inject modules into a workbook"); s.add_argument("workbook"); s.add_argument("ids", nargs="+"); s.add_argument("--out"); s.set_defaults(fn=cmd_add)
    s = sub.add_parser("verify", help="re-hash the LEMMA.* names in a workbook"); s.add_argument("workbook"); s.add_argument("--json", action="store_true"); s.set_defaults(fn=cmd_verify)
    s = sub.add_parser("build-index", help="write the static registry"); s.add_argument("--out", default="dist"); s.set_defaults(fn=cmd_build_index)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    reg = Registry(args.registry) if args.registry else Registry.default()
    try:
        return args.fn(args, reg)
    except (RegistryError, FileNotFoundError) as ex:
        print(f"lemma: {ex}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
