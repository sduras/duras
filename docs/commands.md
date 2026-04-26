# Commands

Full command reference. For quick examples see the [Workflows](workflows.md) page.

---

## Global flags

```sh
duras --version       # print version and exit
duras -c COMMAND      # use encrypted note (.dn.gpg) for this operation
```

`-c` / `--confidential` applies to: `open`, `append`, `show`, `path`.

---

## open

Open a note in `$EDITOR`. Creates the note if it does not exist.

```sh
duras                   # today's note (no subcommand needed)
duras open              # same
duras open 0            # same
duras open -1           # yesterday
duras open 2026-04-01   # absolute date
duras open -- +10       # pass +10 to $EDITOR (e.g. jump to line 10 in vi)
duras -c open           # open encrypted note
```

Arguments after `--` are passed verbatim to the editor.

New notes are opened with the cursor on the first blank line after the header.

---

## append

Append a timestamped line to a note without opening an editor.

```sh
duras append "text"
duras append -d -1 "text"       # append to yesterday
duras append -d 2026-04-01 "x"  # append to absolute date
cat file | duras append -        # read from stdin
duras -c append "secret"         # append to encrypted note
```

`-` reads from stdin. Empty stdin is an error.

The appended line format is:

```
[YYYY-MM-DD HH:MM] text
```

---

## show

Print a note to stdout.

```sh
duras show
duras show -1
duras show 2026-04-01
duras -c show           # decrypt and print encrypted note
```

If both a plain and encrypted note exist for the same date, `show` prints
the plain note and warns. Use `-c` for the encrypted one.

---

## list

List recent notes.

```sh
duras list              # last 10 notes
duras list -n 20        # last 20 notes
duras list -n 0         # all notes
```

Output is sorted by filename (ISO date), newest first. Each line shows:
mtime, size, filename, and a lock symbol for encrypted notes.

---

## search

Search plain notes for a keyword (literal match, not regex).

```sh
duras search "keyword"
duras search "keyword" -i    # case-insensitive
```

Encrypted notes are skipped. A count of skipped notes is printed to stderr.

---

## tags

List all `#tags` found across plain notes, or find notes containing a specific tag.

```sh
duras tags                   # list all tags with occurrence counts
duras tags project           # list notes containing #project
duras tags "#project"        # same; leading # is stripped
```

Tag matching is case-insensitive. Encrypted notes are skipped.

---

## stats

Print summary statistics.

```sh
duras stats
```

Output includes: note counts (plain/encrypted/total), total size, date range,
and current streak (consecutive days with at least one note).

---

## export

Archive notes to a `.tar.gz` file.

```sh
duras export                    # export to current directory
duras export ~/backup           # export to ~/backup/
duras export ~/backup --encrypt # encrypt the archive with gpg
```

Without `--encrypt`, the archive is plaintext. Encrypted `.dn.gpg` files
are included in their encrypted form.

With `--encrypt`, the archive is piped directly into GPG. No plaintext
`.tar.gz` is written to disk.

Output filename: `duras-YYYYMMDD-HHMMSS.tar.gz[.gpg]`

---

## path

Print the absolute path of a note file.

```sh
duras path              # today's plain note path
duras path -1           # yesterday
duras path 2026-04-01
duras -c path           # encrypted note path
```

The file does not need to exist. Useful in scripts:

```sh
wc -w "$(duras path)"
$EDITOR "$(duras path -1)"
```

---

## dir

Print the notes root directory.

```sh
duras dir
```

Useful in scripts:

```sh
grep -r "#todo" "$(duras dir)"
```

---

## today

Print today's date in `YYYY-MM-DD` format.

```sh
duras today
```

---

## audit

Validate the notes directory structure.

```sh
duras audit
```

Checks for: unexpected files or directories, filename/path mismatches,
future-dated notes, broken symlinks, and dates with both `.dn` and `.dn.gpg`
present simultaneously.

Exits with code `1` if any issues are found. Output goes to stdout.

---

## echo

List notes that share the same month and day, across all years.

```sh
duras echo              # notes on today's MM-DD in all years
duras echo 2026-04-01   # notes on April 1 in all years
duras echo -30          # notes on the date 30 days ago, across all years
```

---

## near

List notes within ±3 days of a date.

```sh
duras near              # notes near today
duras near 2026-01-01   # notes near January 1
```

Both plain and encrypted notes are shown.

---

## mv

Move a note from one date to another.

```sh
duras mv 2026-04-20 2026-04-19   # fix a misdated note
```

Only accepts `YYYY-MM-DD` format (no relative offsets).
Moves both `.dn` and `.dn.gpg` if both exist.
The destination date must not already have a note.
Empty source directories are removed after the move.

---

## Date formats

All commands that accept a date accept:

| Format | Example | Meaning |
| ------ | ------- | ------- |
| `YYYY-MM-DD` | `2026-04-01` | Absolute date |
| Integer | `0` | Today |
| Integer | `-1` | Yesterday |
| Integer | `-7` | One week ago |

Future dates are rejected.

---

## Environment variables

| Variable | Default | Meaning |
| -------- | ------- | ------- |
| `DURAS_DIR` | `~/Documents/Notes` | Notes root directory |
| `EDITOR` | nano / vi / ed | Editor command |
| `DURAS_GPG_KEY` | (first secret key) | GPG recipient for encryption |

---

## Exit codes

| Code | Meaning |
| ---- | ------- |
| 0 | Success |
| 1 | Generic error |
| 2 | Note or directory not found |
| 3 | Invalid input |
| 4 | External tool failure (gpg, editor) |
