# duras

[![License](https://img.shields.io/badge/license-ISC-blue)](https://opensource.org/licenses/ISC)

**Daily notes as plain text files, with search and optional encryption**.

---

## Model

One note per day:

```

YYYY/MM/YYYY-MM-DD.dn

```

Properties:

- plain UTF-8 text
- filesystem is the index
- no database, no hidden state
- atomic writes

Encrypted note:

```

YYYY/MM/YYYY-MM-DD.dn.gpg

````

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
- GUI / rich text editor
- query engine or database

---

## Variants

### duras

- system `gpg`
- no dependencies
- Unix-like systems

### duras_ashell

- iOS [a-Shell mini](https://holzschu.github.io/a-Shell_iOS/)
- [PGPy](https://github.com/SecurityInnovation/PGPy) (pure Python)
- no external binaries
- `.asc` key handling (no keyring)
- compatible encrypted format

---

## Usage

```sh
duras
duras append "note"
duras search term
```

---

## Commands

### open

```sh
duras open
duras open -1
duras open 2026-04-19
duras open -- +7
```

### append

```sh
duras append "text"
duras append -d -1 "yesterday"
cat file | duras append -
```

`-` = stdin

---

## Encryption

```sh
duras -c open
duras -c append "secret"
duras -c show
```

Notes:

* uses system `gpg`
* append is memory-only
* editor uses temp file

---

## Search / tags

```sh
duras search error
duras search todo -i
duras tags
```

* literal match (not regex)
* encrypted notes excluded

---

## Listing

```sh
duras list
duras list -n 0
duras stats
```

Order: filename (date), not mtime.

---

## Export

```sh
duras export ~/backup
duras export ~/backup --encrypt
```

Creates archive; optional encryption avoids plaintext export.

---

## Dates

```
YYYY-MM-DD  absolute
0           today
-1          yesterday
+7          future
```

**Future dates are rejected**.

---

## Environment

| var          | meaning                                |
| ------------ | -------------------------------------- |
| DURAS_DIR     | notes dir (default: ~/Documents/Notes) |
| EDITOR       | editor fallback: nano / vi / ed        |
| DURAS_GPG_KEY | encryption recipient                   |

---

## Behavior

* one file per day
* plain + encrypted may coexist
* atomic writes
* no index layer

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

* encrypted notes not searchable
* depends on `gpg`

---

## Docs

* **`man duras`**
* [https://codeberg.org/duras/duras](https://codeberg.org/duras/duras)

---

## License

ISC
