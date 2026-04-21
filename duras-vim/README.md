## duras_bridge.vim — a-shell Vim integration layer

Purpose: minimal bridge between Vim buffer, system clipboard, and `duras` CLI.

No dependencies. No plugin manager required.

---

# 1. Installation

## 1.1 Locate Vim runtime directory

In a-Shell Vim, one of these typically works:

```sh
~/.vim/plugin/
~/.vim/
~/.vimrc + manual sourcing
```

Check:

```vim
:echo $HOME
```

If `.vim/plugin` does not exist:

```sh
mkdir -p ~/.vim/plugin
```

---

## 1.2 Install plugin file

Create file:

```sh
~/.vim/plugin/duras_bridge.vim
```

Paste plugin content.

---

## 1.3 Verify load

Open Vim and run:

```vim
:scriptnames
```

Look for:

```
duras_bridge.vim
```

If missing:

```vim
:source ~/.vim/plugin/duras_bridge.vim
```

---

## 1.4 Prerequisites check

Inside Vim:

```vim
:echo system('duras --version')
```

Expected:

* version string or CLI output

Clipboard test:

```vim
:echo system('pbpaste')
```

If empty or error:

* plugin still works, but clipboard reads fall back to `getreg('+')`

---

# 2. Command reference

## 2.1 Open notes

### Open today

```vim
:DOpen
```

### Open specific date

```vim
:DOpen 2026-04-20
```

### Open by offset

```vim
:DOpen -1
```

Behavior:

* resolves file path via `duras path`
* opens directly in current Vim instance (`:edit`)
* if the note does not exist yet, Vim opens an empty buffer at that path (standard Vim new-file behavior)
* no nested editor processes

---

## 2.2 Append data

### Append current buffer to today

```vim
:DAppend
```

### Append visual selection

1. Select text in visual mode
2. Run:

```vim
:DAppend
```

### Append inline text

```vim
:DAppend meeting notes for Monday
```

No quoting needed. Everything after `:DAppend ` is the text.

### Append clipboard

```vim
:DAppend -
```

Behavior:

* reads from `pbpaste` (iOS system clipboard)
* sends text to `duras append -` via stdin

---

## 2.3 Search notes

```vim
:DSearch keyword
```

Example:

```vim
:DSearch meeting
```

Result:

* opens temporary buffer `[duras-search]`
* `<CR>` on a result line opens the matching note

Navigation:

* `<CR>` → open note
* `:q` → close search buffer

---

## 2.4 Clipboard utilities

### Copy entire buffer → clipboard

```vim
:DClipYank
```

### Paste clipboard below cursor

```vim
:DClipPaste
```

### Copy current note path → clipboard

```vim
:DCopyPath
```

---

## 2.5 Utilities

### Show stats

```vim
:DStats
```

### Show current note path

```vim
:DPath
```

### List all tags

```vim
:DTags
```

### List notes containing a tag

```vim
:DTags project
```

Note: do not prefix with `#`. Pass the bare tag name.

---

# 3. Daily workflows

## 3.1 Quick journaling

Open today:

```vim
:DOpen
```

Append a thought:

```vim
:DAppend meeting notes for Monday
```

Or:

* copy text in Safari
* switch to Vim
* run:

```vim
:DAppend -
```

---

## 3.2 Search-driven retrieval

```vim
:DSearch project x
```

Then:

* move cursor to result
* press `<Enter>`
* note opens directly

---

## 3.3 Clipboard-driven capture

Typical a-Shell flow:

1. Copy text anywhere (Safari, terminal, etc.)
2. In Vim:

```vim
:DAppend -
```

No intermediate files.

---

## 3.4 Navigation without nesting editors

Old behavior (avoided):

* `duras open` → spawns `$EDITOR` → nested Vim

New behavior:

* resolve path via `duras path`
* `:edit file`
* single Vim session only

---

# 4. Keybindings (optional)

## Recommended defaults

```vim
<leader>do  → :DOpen
<leader>da  → :DAppend
<leader>ds  → :DSearch (cursor ready for input)
<leader>dp  → :DPath
```

Visual mode:

```vim
<leader>da  → :DAppend (selection)
```
