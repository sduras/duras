# Installation

## Requirements

- Python 3.9 or later
- Unix-like system (Linux, macOS, OpenBSD, FreeBSD)
- `gpg` — optional, only needed for encrypted notes

---

## pip

```sh
pip install duras
```

Verify:

```sh
duras today
```

### Command not found

If `duras: command not found`, your pip scripts directory is not in `$PATH`.

Find it:

```sh
python3 -m site --user-base
```

Add `<output>/bin` to your `$PATH` in `~/.profile` or `~/.kshrc`:

```sh
export PATH="$HOME/.local/bin:$PATH"
```

### pipx

If you prefer an isolated install:

```sh
pipx install duras
```

---

## Debian / Ubuntu

Download the latest `.deb` from the
[releases page](https://codeberg.org/duras/duras/releases):

```sh
sudo dpkg -i duras_1.0.7_all.deb
```

The `.deb` installs the `duras` command and the `man duras` page.

---

## From source

```sh
git clone https://codeberg.org/duras/duras.git
cd duras
pip install .
```

---

## man page

If installed via pip, the man page may not be in `man`'s search path.

```sh
# find it
find $(python3 -m site --user-base) -name "duras.1" 2>/dev/null

# install
mkdir -p ~/.local/share/man/man1
cp /path/to/duras.1 ~/.local/share/man/man1/
man duras
```

On Linux, run `mandb -q` after copying. Not needed on OpenBSD or macOS.

---

## Upgrading

```sh
pip install --upgrade duras
```

---

## Uninstalling

```sh
pip uninstall duras
```

Your notes directory (`$DURAS_DIR`, default `~/Documents/Notes`) is never
touched by install or uninstall.
