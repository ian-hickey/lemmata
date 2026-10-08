"""A module folder loaded into memory, with spec validation."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

import yaml

from . import canonical

REQUIRED_META = ["id", "name", "version", "summary", "definition", "parameters", "returns", "license"]
ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
PARAM_RE = re.compile(r"^[a-z_][a-z0-9_]*$")
CELL_REF_RE = re.compile(r"(?<![A-Z0-9_.$#])\$?[A-Z]{1,3}\$?[0-9]{1,7}(?![A-Z0-9_(])")
PARAM_TYPES = {"number", "text", "boolean", "range", "any"}
ERROR_LITERAL_RE = re.compile(r"#(?:VALUE!|NUM!|DIV/0!|REF!|NAME\?|NULL!|SPILL!|CALC!|N/A|GETTING_DATA)")
SUMMARY_MAX = 240

BANNED_FUNCTIONS = {
    "WEBSERVICE", "RTD", "NOW", "TODAY", "RAND", "RANDBETWEEN", "RANDARRAY",
    "INDIRECT", "OFFSET", "CELL", "INFO", "HYPERLINK", "FILTERXML", "ENCODEURL",
    "IMAGE", "STOCKHISTORY",
}


@dataclass
class Module:
    path: Path
    meta: dict
    formula: str
    tests: dict
    readme: str = ""
    problems: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path | str) -> "Module":
        path = Path(path)
        meta = yaml.safe_load((path / "module.yaml").read_text(encoding="utf-8")) or {}
        formula = (path / "formula.lambda").read_text(encoding="utf-8")
        tests_file = path / "tests.yaml"
        tests = yaml.safe_load(tests_file.read_text(encoding="utf-8")) if tests_file.exists() else {}
        readme_file = path / "README.md"
        readme = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""
        return cls(path=path, meta=meta, formula=formula, tests=tests or {}, readme=readme)

    # Identity -----------------------------------------------------------

    @property
    def id(self) -> str:
        return str(self.meta.get("id", self.path.name))

    @property
    def name(self) -> str:
        return str(self.meta.get("name", ""))

    @property
    def version(self) -> str:
        return str(self.meta.get("version", ""))

    @property
    def summary(self) -> str:
        return str(self.meta.get("summary", ""))

    @property
    def parameters(self) -> list[dict]:
        return list(self.meta.get("parameters") or [])

    @property
    def dependencies(self) -> list[dict]:
        return list(self.meta.get("dependencies") or [])

    @property
    def cases(self) -> list[dict]:
        return list(self.tests.get("cases") or [])

    @cached_property
    def canonical_formula(self) -> str:
        return canonical.canonical_formula(self.formula)

    @cached_property
    def formula_hash(self) -> str:
        return canonical.formula_hash(self.formula)

    @cached_property
    def module_hash(self) -> str:
        return canonical.module_hash(self.formula, self.meta)

    @property
    def label(self) -> str:
        return f"{self.id}@{self.version} sha256:{self.module_hash}"

    # Validation ---------------------------------------------------------

    def validate(self, prefix: str = "LEMMA.") -> list[str]:
        """Return spec violations. An empty list means the module conforms."""
        errors: list[str] = []
        meta = self.meta
        for key in REQUIRED_META:
            if key not in meta or meta[key] in (None, "", []):
                errors.append(f"module.yaml: missing '{key}'")
        if not ID_RE.match(self.id):
            errors.append(f"module.yaml: id '{self.id}' must match {ID_RE.pattern}")
        if self.id != self.path.name:
            errors.append(f"module.yaml: id '{self.id}' does not match folder name '{self.path.name}'")
        if not self.name.startswith(prefix) or self.name != self.name.upper():
            errors.append(f"module.yaml: name '{self.name}' must start with '{prefix}' and be upper case")
        if not VERSION_RE.match(self.version):
            errors.append(f"module.yaml: version '{self.version}' is not MAJOR.MINOR.PATCH")
        if "\n" in self.summary.strip() or len(self.summary) > SUMMARY_MAX:
            errors.append(f"module.yaml: summary must be one line of at most {SUMMARY_MAX} characters")
        definition = meta.get("definition") or {}
        if not isinstance(definition, dict) or not definition.get("source"):
            errors.append("module.yaml: definition.source is required")
        returns = meta.get("returns") or {}
        if not isinstance(returns, dict) or not returns.get("type"):
            errors.append("module.yaml: returns.type is required")

        try:
            params = canonical.lambda_parameters(self.formula)
        except ValueError as ex:
            errors.append(f"formula.lambda: {ex}")
            params = []
        declared = [p.get("name") for p in self.parameters if isinstance(p, dict)]
        if params and declared != params:
            errors.append(f"module.yaml: parameters {declared} do not match LAMBDA parameters {params}")
        for p in params:
            if not PARAM_RE.match(p):
                errors.append(f"formula.lambda: parameter '{p}' must match {PARAM_RE.pattern}")
            if CELL_REF_RE.fullmatch(p.upper()):
                errors.append(f"formula.lambda: parameter '{p}' looks like a cell reference")
        for p in self.parameters:
            if not isinstance(p, dict):
                errors.append("module.yaml: each parameter must be a mapping")
                continue
            if p.get("type") not in PARAM_TYPES:
                errors.append(f"module.yaml: parameter '{p.get('name')}' type must be one of {sorted(PARAM_TYPES)}")
            if not p.get("description"):
                errors.append(f"module.yaml: parameter '{p.get('name')}' needs a description")

        masked = ERROR_LITERAL_RE.sub("", canonical.mask_strings(self.canonical_formula))
        calls = canonical.function_calls(self.formula)
        banned = sorted(c for c in calls if c in BANNED_FUNCTIONS or c.startswith("CUBE"))
        if banned:
            errors.append(f"formula.lambda: banned functions {banned}")
        if "!" in masked:
            errors.append("formula.lambda: sheet or external references ('!') are not allowed")
        if "[" in masked:
            errors.append("formula.lambda: structured or external references ('[') are not allowed")
        m = CELL_REF_RE.search(masked)
        if m:
            errors.append(f"formula.lambda: cell reference '{m.group(0)}' is not allowed")

        if not self.cases:
            errors.append("tests.yaml: at least one case is required")
        for i, case in enumerate(self.cases):
            if not isinstance(case, dict) or "inputs" not in case or "expect" not in case:
                errors.append(f"tests.yaml: case {i} needs 'inputs' and 'expect'")
            elif not isinstance(case["inputs"], list):
                errors.append(f"tests.yaml: case {i} 'inputs' must be a list")
        for d in self.dependencies:
            if not isinstance(d, dict) or not d.get("id") or not d.get("module_hash"):
                errors.append("module.yaml: each dependency needs 'id' and 'module_hash'")
        return errors

    def to_index_entry(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "summary": self.summary,
            "formula_hash": self.formula_hash,
            "module_hash": self.module_hash,
            "parameters": self.parameters,
            "returns": self.meta.get("returns"),
            "tags": self.meta.get("tags") or [],
            "dependencies": self.dependencies,
            "label": "tested",
            "path": f"modules/{self.module_hash}/",
        }
