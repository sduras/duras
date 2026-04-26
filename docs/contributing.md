# Contributing

## Repository layout

```
duras/
├── duras/
│   ├── __init__.py
│   ├── core.py          ← all domain logic
│   └── cli.py           ← argument parsing and dispatch only
├── duras-ashell/
│   └── duras_ashell.py  ← standalone iOS variant
├── man/
│   └── duras.1          ← man page (mdoc format)
├── debian/              ← Debian package metadata
├── docs/                ← this documentation
├── pyproject.toml
├── LICENSE
└── README.md
```

`core.py` is the library. `cli.py` is the interface. They are kept separate
so `core.py` can be imported by scripts without pulling in argparse or
touching `sys.argv`. `duras_ashell.py` is self-contained and shares no code
with the main package.

---

## Dev setup

```sh
git clone https://codeberg.org/duras/duras.git
cd duras
pip install -e .
duras today
```

---

## Code conventions

- No external dependencies in `core.py` or `cli.py`. stdlib only.
- No abstractions for single-use code.
- Match existing style when editing existing functions.
- Exceptions: use `DurasError` subclasses with the appropriate `exit_code`.
- Type annotations required on all function signatures (mypy strict).

---

## Type checking

```sh
pip install mypy
mypy duras/core.py duras/cli.py
```

---

## Man page

Edit `man/duras.1` directly (mdoc format). Preview:

```sh
man ./man/duras.1
```

On Linux with groff:

```sh
groff -Tascii -mdoc man/duras.1 | less
```

---

## Submitting changes

1. Fork the repository on Codeberg.
2. Create a branch for your change.
3. Keep commits focused: one logical change per commit.
4. Open a pull request with a plain description of what changed and why.

For bug reports: open an issue at
[codeberg.org/duras/duras/issues](https://codeberg.org/duras/duras/issues)
with the output of `duras --version` and the exact command that failed.

---

## Release process

1. Bump `version` in `pyproject.toml`.
2. `git commit -m "release X.Y.Z"` and `git tag vX.Y.Z`.
3. `git push origin main && git push origin vX.Y.Z`.
4. `rm -rf dist/ && python -m build`.
5. `twine upload dist/duras-X.Y.Z*`.
6. Create a release on Codeberg, attach the files from `dist/`.
