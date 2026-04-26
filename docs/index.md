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

## Model

One note per day, stored as a plain text file:

```
~/Documents/Notes/
└── YYYY/
    └── MM/
        └── YYYY-MM-DD.dn
```

- Plain UTF-8 text
- Filesystem is the index
- No database, no hidden state
- Atomic writes

Encrypted notes use the `.dn.gpg` extension and are stored alongside plain notes.

---

## Scope

Fits:

- Terminal-based workflows
- Grep-based retrieval
- Long-lived plain text notes
- Optional encryption via GPG

Not a fit:

- Sync system
- GUI or rich text editor
- Query engine or database
- Task manager or knowledge base

---

## Design principle

Every addition to duras must satisfy:

> Does this make the data more trustworthy, durable, or understandable in 10 years?

If not, it is out of scope. If duras disappears, your notes remain readable and
recoverable with standard Unix tools.

---

## Links

- [Codeberg repository](https://codeberg.org/duras/duras)
- [PyPI](https://pypi.org/project/duras/)
- [Issue tracker](https://codeberg.org/duras/duras/issues)
