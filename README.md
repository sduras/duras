# duras

[![License](https://img.shields.io/badge/license-ISC-blue)](https://opensource.org/licenses/ISC)

**Daily notes as plain text files, with search and optional encryption.**

Standalone tool, but most effectively used together with [duras_bridge](https://codeberg.org/duras/duras_bridge), a minimal [Vim](https://www.vim.org/) / [Neovim](https://neovim.io/) plugin that integrates the CLI directly into the text editor.

---

## Install

```sh
pip install duras
```

Requires Python 3.9 or later. No dependencies. `gpg` optional for encrypted notes.

---

## Quick start

```sh
duras                          # open today's note in $EDITOR
duras append "fix login bug #todo"
duras search todo
duras tags
```

---

## Note format

One file per day:

```
~/Documents/Notes/YYYY/MM/YYYY-MM-DD.dn
```

Each note is self-describing plain UTF-8 text:

```
date: 2026-04-28

2026-04-28 09:10  started work
2026-04-28 14:32  fix null check in login handler #todo
2026-04-28 16:00  called bank re: account — follow up Thursday
```

Properties:

- plain UTF-8, LF line endings
- header `date:` field matches filename and directory
- entries are timestamped lines, two spaces between timestamp and text
- filesystem is the index; no database, no hidden state
- atomic writes
- readable with any text tool

Encrypted note:

```
YYYY/MM/YYYY-MM-DD.dn.gpg
```

via the [GNU Privacy Guard](https://gnupg.org/).

---

## Scope

Fits:

- terminal-based workflows
- grep-based retrieval
- long-lived plain text notes
- optional encryption

Not a fit:

- sync system
- GUI or rich text editor
- query engine or database

---

## Commands

### open

```sh
duras               # today
duras open -1       # yesterday
duras open 2026-04-19
duras open -- +10   # pass +10 to $EDITOR (jump to line)
```

### append

```sh
duras append "text"
duras append -d -1 "yesterday"
cat file | duras append
cmd | duras append
```

Text argument is optional. When omitted, stdin is read automatically.

### show

```sh
duras show
duras show -1
```

### list / stats

```sh
duras list
duras list -n 0     # all notes
duras stats
```

Order: by filename (ISO date), not mtime.

### search / tags

```sh
duras search error
duras search todo -i    # case-insensitive
duras tags              # all tags with counts
duras tags project      # notes containing #project
```

Literal match, not regex. Encrypted notes excluded.

### export

```sh
duras export ~/backup
duras export ~/backup --encrypt
```

Creates a timestamped `.tar.gz`. `--encrypt` pipes through `gpg`; no plaintext archive is written.

### other

```sh
duras path          # absolute path to today's note
duras dir           # notes root directory
duras today         # print today's date
duras audit         # validate directory structure
duras echo          # notes on this date in past years
duras near          # notes within ±3 days of today
duras mv 2026-04-17 2026-04-16
```

---

## Encryption

```sh
duras -c open
duras -c append "secret"
duras -c show
```

- uses system `gpg`
- `append -c` is memory-only; no plaintext temp file
- `open -c` writes a temp file to `/dev/shm` when available

---

## Dates

```
YYYY-MM-DD   absolute
0            today
-1           yesterday
-7           one week ago
```

Future dates are rejected.

---

## Environment

| variable        | meaning                                      |
| --------------- | -------------------------------------------- |
| `DURAS_DIR`     | notes directory (default: ~/Documents/Notes) |
| `EDITOR`        | editor (fallback: nano, vi, ed)              |
| `DURAS_GPG_KEY` | GPG recipient (default: self)                |

`.editorconfig` is written to the notes directory on first run. It configures
any supporting editor to use UTF-8, LF line endings, and 72-column line length
for `.dn` files.

---

## Exit codes

| code | meaning          |
| ---- | ---------------- |
| 0    | ok               |
| 1    | error            |
| 2    | not found        |
| 3    | invalid input    |
| 4    | external failure |

---

## Limits

- encrypted notes are not searchable
- depends on system `gpg` for encryption

---

## Docs

- `man duras`
- `duras --help`
- <https://duras.readthedocs.io/en/latest/>

---

## Variants

### duras

Standard variant for Unix-like systems. Uses system `gpg`. No dependencies.

### duras_ashell

For iOS [a-Shell mini](https://holzschu.github.io/a-Shell_iOS/). Uses [PGPy](https://github.com/SecurityInnovation/PGPy) instead of system `gpg`. No external binaries. Handles `.asc` keys directly; no keyring. Compatible encrypted format.

---

## License

ISC License
