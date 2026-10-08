"""The set of modules in a repo checkout, plus advisories."""

from __future__ import annotations

import io
import json
import os
import tarfile
import urllib.request
from functools import cached_property
from pathlib import Path

import yaml

from .module import Module

DEFAULT_REGISTRY_URL = "https://ian-hickey.github.io/lemmata/"


class RegistryError(KeyError):
    pass


class Registry:
    def __init__(self, root: Path | str, prefix: str = "LEMMA."):
        self.root = Path(root)
        self.prefix = prefix
        self.modules_dir = self.root / "modules"
        self.advisories_dir = self.root / "advisories"

    @classmethod
    def default(cls) -> "Registry":
        """The registry to use: LEMMATA_REGISTRY (a path or URL), else this checkout, else the public site."""
        setting = os.environ.get("LEMMATA_REGISTRY") or os.environ.get("LEMMATA_REGISTRY_ROOT")
        if setting:
            return RemoteRegistry(setting) if setting.startswith(("http://", "https://")) else cls(setting)
        checkout = Path(__file__).resolve().parents[2]
        if (checkout / "modules").is_dir():
            return cls(checkout)
        return RemoteRegistry(DEFAULT_REGISTRY_URL)

    @cached_property
    def modules(self) -> list[Module]:
        found = []
        if not self.modules_dir.exists():
            return found
        for folder in sorted(self.modules_dir.iterdir()):
            if (folder / "module.yaml").exists():
                found.append(Module.load(folder))
        return found

    def describe(self) -> str:
        return str(self.root)

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


class RemoteRegistry(Registry):
    """A published registry (index.json plus one tarball per module hash), cached on disk.

    Every downloaded module is re-hashed and must match the hash it was fetched by.
    """

    def __init__(self, url: str, cache_dir: Path | str | None = None, prefix: str = "LEMMA."):
        self.url = url.rstrip("/") + "/"
        cache = Path(cache_dir or os.environ.get("LEMMATA_CACHE") or Path.home() / ".cache" / "lemmata")
        super().__init__(cache, prefix=prefix)

    def describe(self) -> str:
        return self.url

    def _fetch(self, path: str) -> bytes:
        with urllib.request.urlopen(self.url + path, timeout=30) as resp:  # noqa: S310 (fixed https base)
            return resp.read()

    @cached_property
    def index(self) -> dict:
        data = json.loads(self._fetch("index.json").decode("utf-8"))
        if data.get("prefix"):
            self.prefix = data["prefix"]
        return data

    def _materialize(self, entry: dict) -> Path:
        dest = self.modules_dir / entry["module_hash"]
        if (dest / "module.yaml").exists():
            return dest
        archive = entry.get("archive") or f"modules/{entry['module_hash']}.tar.gz"
        data = self._fetch(archive)
        self.modules_dir.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
            tar.extractall(self.modules_dir, filter="data")
        return dest

    @cached_property
    def modules(self) -> list[Module]:
        found = []
        for entry in self.index.get("modules", []):
            mod = Module.load(self._materialize(entry))
            if mod.module_hash != entry["module_hash"]:
                raise RegistryError(f"{entry['id']}: downloaded module hashes to {mod.module_hash[:12]}, index says {entry['module_hash'][:12]}")
            found.append(mod)
        return found

    @cached_property
    def advisories(self) -> list[dict]:
        return list(self.index.get("advisories", []))
