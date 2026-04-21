# duras_bridge.vim plugin

**Purpose**: minimal bridge between [Vim](https://www.vim.org/) buffer, system clipboard, and `duras` CLI.

No dependencies. No plugin manager required.

---

##  Installation

### Locate Vim runtime directory

In a-shell Vim, one of these typically works:

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

### Install plugin

Create file:

```sh
~/.vim/plugin/duras_bridge.vim
```

Paste plugin content.

---

### Verify load

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

### Prerequisites check

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

* plugin still works, but clipboard fallback will rely on `getreg('+')`

---

## Command reference

### Open today

```vim
:DOpen
```

### Open specific date

```vim
:DOpen 2026-04-20
```

---

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

### Append clipboard

```vim
:DAppend -
```

---

### Search notes

```vim
:DSearch keyword
```

Example:

```vim
:DSearch meeting
```

Result:

* opens temporary buffer `[duras-search]`
* Enter on a line opens matching note

Navigation:

* `<CR>` → open note
* `:q` → close search buffer

---

### Copy buffer → clipboard

```vim
:DClipYank
```

### Paste clipboard below cursor

```vim
:DClipPaste
```

### Copy current note path

```vim
:DCopyPath
```

---

### Show stats

```vim
:DStats
```

### Show current note path

```vim
:DPath
```

---


## Recommended keybindings

```vim
<leader>do  → open note
<leader>da  → append
<leader>ds  → search
<leader>dp  → path
```

Visual mode:

```vim
<leader>da  → append selection
```

---

