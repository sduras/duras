## duras_bridge.vim

Minimal Vim bridge for the `duras` CLI.
Connects buffer, clipboard, and notes. No dependencies.

---

## Installation

Copy the plugin file:

```sh
mkdir -p ~/.vim/plugin
cp duras_bridge.vim ~/.vim/plugin/
```

Verify load:

```vim
:scriptnames
```

---

## Requirements

Inside Vim:

```vim
:echo system('duras --version')
```

Clipboard (optional, iOS):

```vim
:echo system('pbpaste')
```

Falls back to `getreg('+')` if unavailable.

---

## Commands

### Open

```vim
:DOpen            " today
:DOpen 2026-04-20
:DOpen -1         " offset
```

Opens via `:edit` using `duras path`.
Creates file implicitly if missing.

---

### Append

```vim
:DAppend                 " buffer
:DAppend some text       " inline
:DAppend -               " clipboard
```

Visual mode:

```vim
:'<,'>DAppend
```

---

### Search

```vim
:DSearch keyword
```

Results open in `[duras-search]`.

* `<CR>` open note
* `:q` close

---

### Clipboard

```vim
:DClipYank     " buffer → clipboard
:DClipPaste    " clipboard → buffer
:DCopyPath     " note path → clipboard
```

---

### Info

```vim
:DStats
:DPath
:DTags
:DTags project
```

Tags: pass bare name (no `#`).

---

## Usage

### Journal

```vim
:DOpen
:DAppend quick note
:DAppend -
```

---

### Search → open

```vim
:DSearch project
```

`<CR>` on result.

---

### Clipboard capture

Copy anywhere → in Vim:

```vim
:DAppend -
```

---

## Notes

* No nested editors (`:edit` only)
* Works with non-existent files (standard Vim behavior)
* Designed for a-shell workflows

---

## Optional mappings

```vim
nnoremap <leader>do :DOpen<CR>
nnoremap <leader>da :DAppend<CR>
nnoremap <leader>ds :DSearch 
nnoremap <leader>dp :DPath<CR>

vnoremap <leader>da :DAppend<CR>
```

