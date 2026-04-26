# Changelog

## 1.0.7

- Fix vi/nvi "Illegal address" error on OpenBSD when opening a new note
  (`+4` cursor position on a 3-line file corrected to `+3`)

## 1.0.6

- Lower `requires-python` from `>=3.13` to `>=3.9` (actual language floor)
- Add full classifier list to `pyproject.toml`
- Add `[project.urls]` block

## 1.0.5 – 1.0.1

- PyPI packaging fixes and metadata updates

## 1.0.0

- Renamed from `hisa` to `duras`
- Renamed all environment variables: `HISA_DIR` → `DURAS_DIR`, `HISA_GPG_KEY` → `DURAS_GPG_KEY`
- Renamed all exception classes: `HisaError` → `DurasError`, etc.
- Version reset to 1.0.0

## 0.6.0 (hisa)

- Final release under the `hisa` name
- `echo` and `near` subcommands
- `mv` subcommand for moving misdated notes
- `audit` subcommand
