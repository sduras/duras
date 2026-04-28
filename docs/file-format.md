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
- The `date:` header field must match the enclosing `YYYY/MM/` path and filename.
- No future-dated notes.
- No date with both `.dn` and `.dn.gpg` present simultaneously.
- No broken symlinks at any level.

**duras** creates directories as needed and never creates files outside this
structure.

---

## Plain note (.dn)

UTF-8 plain text, LF line endings. The header is always exactly one line:

```
date: YYYY-MM-DD
```

A blank line follows the header. Entries written by `duras append` appear
on subsequent lines:

```
date: 2026-04-28

2026-04-28 09:10  started work
2026-04-28 14:32  fix null check in login handler #todo
2026-04-28 16:00  called bank re: account — follow up Thursday
```

The two-space separator between timestamp and text enables clean extraction
with standard tools:

```sh
grep "^date: 2026-04" *.dn        # find all April 2026 notes
grep "^2026-04-28" *.dn           # find all entries for a date
awk '{print substr($0,18)}' *.dn  # extract text from entries
```

Files edited directly with other tools are read without complaint. The
header is a convention; duras does not parse note content beyond the
`date:` field.

---

## Backward compatibility

Notes written by duras 1.0.x used a different header and entry format:

```
2026-04-27
14:32

[2026-04-27 14:32] text of entry
```

These notes remain fully readable as plain text. duras 1.1.0 does not
migrate existing notes. Old and new format notes coexist in the same
directory without issue.

---

## Encrypted note (.dn.gpg)

A GPG-encrypted blob whose decrypted content is identical in format to a
plain `.dn` file. Decrypt with any GPG-compatible tool:

```sh
gpg --decrypt ~/Documents/Notes/2026/04/2026-04-28.dn.gpg
```

---

## .editorconfig

On first run, duras writes a `.editorconfig` file to the notes root:

```ini
[*.dn]
charset = utf-8
end_of_line = lf
insert_final_newline = true
max_line_length = 72
```

Written once to the notes directory on first run. Configures 
supporting editors (Neovim 0.9+, VS Code, JetBrains) to use UTF-8,
LF line endings, and 72-column line length for .dn files. The file
is written once and never modified by duras.

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
# find all notes containing a tag
grep -rl "#todo" "$(duras dir)"

# list all entries across all notes, sorted by timestamp
grep -h "^2026-" "$(duras dir)"/**/*.dn | sort

# word count across all notes
find "$(duras dir)" -name "*.dn" | xargs wc -w | tail -1

# open a specific note directly
$EDITOR ~/Documents/Notes/2026/04/2026-04-01.dn
```

Encrypted notes (`.dn.gpg`) require the GNU Privacy Guard for access.
