# Workflows

Practical patterns for daily use.

---

## Daily capture

Open today's note once in the morning:

```sh
duras
```

Quick captures without opening an editor:

```sh
duras append "called bank re: account — follow up Thursday"
duras append "article to read: example.com/post #reading"
duras append "fix null check in login handler #todo"
```

Pipe command output directly:

```sh
df -h | duras append
git log --oneline -10 | duras append
```

---

## Tagging

Tags are `#word` tokens anywhere in note text, collected by `duras tags` with no configuration. Any word prefixed with `#` becomes a tag — no setup, no schema.

A practical starting set:

| Tag | Meaning |
|---|---|
| `#task` | Actionable item |
| `#done` | Completed task |
| `#idea` | Thought to revisit |
| `#ref` | Reference to keep |
| `#read` | Article or book to read |
| `#waiting` | Blocked on someone else |
| `#buy` | Item to purchase |
| `#log` | Factual record |

Tags are just text. `duras tags task` finds every note containing `#task`. `grep -r "#task" "$(duras dir)"` does the same without duras. No tag has special meaning to the tool — the system is entirely what you make of it.

Find all notes with open items:

```sh
duras tags todo
```

---

## Weekly review

List last week's notes:

```sh
duras list -n 7
```

Print all entries across the last week:

```sh
for i in -6 -5 -4 -3 -2 -1 0; do duras show $i; echo "---"; done | less
```

---

## Searching

```sh
duras search "login bug"
duras search todo -i         # case-insensitive
```

For more complex queries, use grep directly against the entry format:

```sh
# all entries matching a keyword
grep -r "^2026-" "$(duras dir)" | grep "keyword"

# files containing a tag
grep -rl "#todo" "$(duras dir)"

# entries from a specific month
grep -h "^2026-04-" "$(duras dir)"/**/*.dn | sort
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

All entries across all notes, sorted:

```sh
grep -rh "^2026-" "$(duras dir)"/**/*.dn | sort
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
