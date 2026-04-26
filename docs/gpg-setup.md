# GPG Setup

Encryption is optional. Plain notes work without any GPG configuration.

---

## Prerequisites

`gpg` must be installed and on `$PATH`:

```sh
gpg --version
```

| System | Install command |
| ------ | --------------- |
| Debian / Ubuntu | `sudo apt install gnupg` |
| macOS (Homebrew) | `brew install gnupg` |
| OpenBSD | `pkg_add gnupg` |
| FreeBSD | `pkg install gnupg` |

---

## Do you already have a key?

```sh
gpg --list-secret-keys
```

If output is non-empty, you have a key. Note the email address or key ID
and skip to [Set DURAS_GPG_KEY](#set-duras_gpg_key).

---

## Generate a key

```sh
gpg --full-generate-key
```

Recommended choices:

- Key type: `ECC (sign and encrypt)` or `RSA and RSA`
- Key size (RSA only): 4096
- Expiry: your preference; `0` = no expiry
- Real name and email: used to identify the key

The fingerprint appears in the output:

```
pub   ed25519 2026-04-20 [SC]
      ABC123DEF456...
uid   Your Name <you@example.com>
```

---

## Set DURAS_GPG_KEY

Add to your shell profile (`~/.profile`, `~/.kshrc`, `~/.bashrc`):

```sh
export DURAS_GPG_KEY="you@example.com"
```

You can use the email address, the full fingerprint, or a short key ID.
Email is the most readable.

If `DURAS_GPG_KEY` is not set, GPG uses the default recipient (your first
secret key). This works but is less explicit.

Reload your profile:

```sh
. ~/.profile
```

---

## Test the setup

Write an encrypted note:

```sh
duras -c append "test entry"
```

Read it back:

```sh
duras -c show
```

Verify the file on disk is not readable as plaintext:

```sh
cat $(duras -c path)
```

Output should be a PGP block, not your text.

---

## Passphrase and gpg-agent

GPG prompts for your key passphrase on first use per session.
`gpg-agent` caches it for subsequent operations.

On most systems `gpg-agent` starts automatically. On OpenBSD, start it
explicitly in your shell profile:

```sh
eval $(gpg-agent --daemon)
```

---

## Troubleshooting

**`gpg: command not found`** — install gnupg (see Prerequisites above).

**`gpg: no default recipient`** — set `DURAS_GPG_KEY`, or verify you have
a secret key with `gpg --list-secret-keys`.

**`gpg encryption failed`** — run `duras -c append "test"` and observe the
full error. Common causes: key expired, key not trusted, wrong recipient.

**`gpg decryption failed`** — the note was encrypted to a different key,
or the key is not in your keyring.
