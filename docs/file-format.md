# File Format

The on-disk layout and file structure. Useful for writing scripts against
your notes, or for understanding what `duras audit` validates.

---

## Directory layout

```
$DURAS_DIR/              (default: ~/Documents/Notes)
└── YYYY/
    └── MM/
        ├── YYYY-MM-DD.dn
        └── YYYY-MM-DD.dn.gpg
```

Rules enforced by `duras audit`:

- Only `YYYY/` directories at the notes root (four-digit year).
- Only `MM/` directories inside each year directory (two-digit, 01–12).
- Only files named `YYYY-MM-DD.dn` or `YYYY-MM-DD.dn.gpg` inside month directories.
- The date in the filename must match the enclosing `YYYY/MM/` path.
- No future-dated notes.
- No date with both `.dn` and `.dn.gpg` present simultaneously.
- No broken symlinks at any level.

duras creates directories as needed and never creates files outside this
structure.

---

## Plain note (.dn)

UTF-8 plain text. Header written for a new note opened on the current day:

```
2026-04-20
14:32

```

Header written for a note opened on a past date:

```
2026-04-18
created: 2026-04-20 14:32

```

Appended lines (via `duras append`) follow this format:

```
[2026-04-20 15:10] text of the appended entry
```

The header is a convention, not enforced. Files edited directly with other
tools are read without complaint.

---

## Encrypted note (.dn.gpg)

A GPG-encrypted blob whose decrypted content is identical in format to a
plain `.dn` file. The encryption format is standard GPG; the file can be
decrypted with any GPG-compatible tool:

```sh
gpg --decrypt ~/Documents/Notes/2026/04/2026-04-20.dn.gpg
```

---

## File permissions

| Path | Mode |
| ---- | ---- |
| Notes root directory | `0700` (enforced on startup) |
| `.dn` and `.dn.gpg` files | `0600` |
| Temp files during atomic write | `0600` |

---

## Atomic writes

All writes use a write-to-temp-then-rename pattern:

1. Create a temp file (`.duras-XXXXXX`) in the same directory as the target.
2. Write content and `fsync`.
3. Set permissions to `0600`.
4. `os.replace()` — atomic rename on POSIX systems.
5. `fsync` the directory file descriptor.

On failure the temp file is unlinked. A partial write never replaces an
existing note.

---

## Using notes without duras

Because notes are plain UTF-8 files, standard Unix tools work directly:

```sh
# full-text search
grep -r "keyword" "$(duras dir)"

# list all note files sorted by date
find "$(duras dir)" -name "*.dn" | sort

# word count across all notes
find "$(duras dir)" -name "*.dn" | xargs wc -w | tail -1

# open a specific note directly
$EDITOR ~/Documents/Notes/2026/04/2026-04-01.dn
```

Encrypted notes (`.dn.gpg`) require GPG for access.
