# Changelog

## 1.1.0

- New note header format: single field `date: YYYY-MM-DD`; removed
  `created:` field (redundant with first entry timestamp)
- New entry format: `YYYY-MM-DD HH:MM  text` (two spaces, no brackets);
  improves grep-ability and matches log conventions
- `append`: TEXT argument is now optional; omitting it reads from stdin,
  allowing `cmd | duras append` without the trailing `-`
- Normalize stdin/multi-line text on append: strip trailing whitespace
  per line, collapse consecutive blank lines, convert tabs to spaces
- Apply same normalization and future-date guard to confidential append
- Write `.editorconfig` to notes directory on first run (utf-8, lf,
  `insert_final_newline`, `max_line_length=72`)
- Editor cursor always positioned at line 2 on new notes (header is
  always one line plus one blank line)
- Drop planned `duras sync` command (risk/benefit not acceptable).

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
