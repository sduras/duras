# duras

**Daily notes as plain text files, with search and optional encryption.**

---

## Quick start

```sh
pip install duras

duras                        # open today's note in $EDITOR
duras append "text #tag"     # quick capture
duras search keyword         # search plain notes
duras tags                   # list all tags
duras -c open                # open encrypted note
```

---

## Note format

One file per day, stored as plain UTF-8 text:

```
~/Documents/Notes/YYYY/MM/YYYY-MM-DD.dn
```

A note is fully self-describing without its filename or directory context:

```
date: 2026-04-28

2026-04-28 09:10  started work
2026-04-28 14:32  fix null check in login handler #todo
2026-04-28 16:00  called bank re: account — follow up Thursday
```

- The `date:` header field names the day the file belongs to
- Entries are timestamped lines; two spaces separate timestamp from text
- Plain UTF-8, LF line endings, no hidden state, atomic writes
- Readable with any text tool; no duras required to read your notes

See [File Format](file-format.md) for the complete specification.

---

## Scope

Fits:

- Terminal-based workflows
- Grep-based retrieval
- Long-lived plain text notes
- Optional encryption via GNU Privacy Guard

Not a fit:

- Sync system
- GUI or rich text editor
- Query engine or database
- Task manager or knowledge base

---

## Design principle

Every addition to duras must satisfy:

> Does this make the data more trustworthy, durable, or understandable in 10 years?

If duras disappears, your notes remain readable and recoverable with
standard Unix tools.

---

## Links

- [Codeberg repository](https://codeberg.org/duras/duras)
- [PyPI](https://pypi.org/project/duras/)
- [Issue tracker](https://codeberg.org/duras/duras/issues)
- [Vim / Neovim integration](https://www.vim.org/scripts/script.php?script_id=6184)
