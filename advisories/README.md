# Advisories

When a published module turns out to be wrong, add one YAML file here:

```yaml
id: 2026-001
module_id: cagr
module_hash: <sha256 of the affected version>
severity: high            # low | medium | high
summary: One line on what is wrong and who is affected.
fixed_version: 0.2.0      # or null if no fix exists yet
```

`af verify` flags any workbook that uses an affected hash.
