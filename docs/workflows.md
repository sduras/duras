# Workflows

Concrete patterns for daily use.

---

## Daily capture

Open today's note once in the morning:

```sh
duras
```

For quick captures without opening an editor:

```sh
duras append "called bank re: account — follow up Thursday"
duras append "article to read: example.com/post #reading"
duras append "fix null check in login handler #todo"
```

Pipe command output directly into a note:

```sh
df -h | duras append -
git log --oneline -10 | duras append -
```

---

## Tagging

Tags are `#word` tokens anywhere in note text, collected by `duras tags`
with no configuration.

A minimal system that works well:

| Tag | Meaning |
| --- | ------- |
| `#todo` | Action item, not yet done |
| `#done` | Completed item |
| `#reading` | Article or book to read |
| `#idea` | Loose thought to revisit |
| `#ref` | Reference to keep |

Find all notes with open items:

```sh
duras tags todo
```

Count how often each tag appears:

```sh
duras tags
```

---

## Weekly review

List last week's notes:

```sh
duras list -n 7
```

Print all of last week to stdout:

```sh
for i in -6 -5 -4 -3 -2 -1 0; do duras show $i; echo "---"; done | less
```

---

## Searching

```sh
duras search "login bug"
duras search todo -i         # case-insensitive
```

For more complex queries, use `grep` directly:

```sh
grep -r "keyword" "$(duras dir)"
grep -rl "#todo" "$(duras dir)"    # files containing #todo
```

Count lines across all notes:

```sh
find "$(duras dir)" -name "*.dn" | xargs wc -l
```

---

## Temporal patterns

Notes written on this date in previous years:

```sh
duras echo
```

Notes around a specific date (±3 days):

```sh
duras near 2026-01-15
```

---

## Backup

```sh
duras export ~/Backups
duras export ~/Backups --encrypt
```

Automate with cron:

```
0 22 * * * duras export ~/Backups
```

---

## Shell integration

Word count of today's note:

```sh
wc -w "$(duras path)"
```

Print today's date in scripts:

```sh
TODAY=$(duras today)
```

---

## Fixing a misdated note

```sh
duras mv 2026-04-20 2026-04-19
```

Both plain and encrypted variants are moved if they exist.
