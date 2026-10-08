"""The set of modules in a repo checkout, plus advisories."""

from __future__ import annotations

import os
from functools import cached_property
from pathlib import Path

import yaml

from .module import Module


class RegistryError(KeyError):
    pass


class Registry:
    def __init__(self, root: Path | str, prefix: str = "AF."):
        self.root = Path(root)
        self.prefix = prefix
        self.modules_dir = self.root / "modules"
        self.advisories_dir = self.root / "advisories"

    @classmethod
    def default(cls) -> "Registry":
        root = os.environ.get("AF_REGISTRY_ROOT")
        if root:
            return cls(root)
        return cls(Path(__file__).resolve().parents[2])

    @cached_property
    def modules(self) -> list[Module]:
        found = []
        if not self.modules_dir.exists():
            return found
        for folder in sorted(self.modules_dir.iterdir()):
            if (folder / "module.yaml").exists():
                found.append(Module.load(folder))
        return found

    def get(self, key: str) -> Module:
        """Find by id, by defined name, or by a prefix of either hash."""
        k = key.strip()
        for m in self.modules:
            if m.id == k or m.name.upper() == k.upper():
                return m
        if len(k) >= 8:
            for m in self.modules:
                if m.module_hash.startswith(k.lower()) or m.formula_hash.startswith(k.lower()):
                    return m
        raise RegistryError(f"no module matches '{key}'")

    def by_formula_hash(self, h: str) -> Module | None:
        return next((m for m in self.modules if m.formula_hash == h), None)

    def by_module_hash(self, h: str) -> Module | None:
        return next((m for m in self.modules if m.module_hash == h), None)

    def with_dependencies(self, modules: list[Module]) -> list[Module]:
        """Modules plus everything they depend on, dependencies first, no duplicates."""
        ordered: list[Module] = []
        seen: set[str] = set()

        def visit(m: Module, stack: tuple[str, ...]) -> None:
            if m.id in stack:
                raise RegistryError(f"dependency cycle: {' -> '.join(stack + (m.id,))}")
            if m.id in seen:
                return
            for dep in m.dependencies:
                target = self.by_module_hash(dep["module_hash"]) or self.get(dep["id"])
                if target.module_hash != dep["module_hash"]:
                    raise RegistryError(
                        f"{m.id} depends on {dep['id']}@{dep['module_hash'][:12]} "
                        f"but the registry has {target.module_hash[:12]}"
                    )
                visit(target, stack + (m.id,))
            seen.add(m.id)
            ordered.append(m)

        for m in modules:
            visit(m, ())
        return ordered

    @cached_property
    def advisories(self) -> list[dict]:
        found = []
        if not self.advisories_dir.exists():
            return found
        for f in sorted(self.advisories_dir.glob("*.yaml")):
            data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
            data.setdefault("id", f.stem)
            found.append(data)
        return found

    def advisories_for(self, module_hash: str) -> list[dict]:
        return [a for a in self.advisories if a.get("module_hash") == module_hash]
