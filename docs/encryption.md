# Encryption

## What is protected

The note content. Everything written to a `.dn.gpg` file is encrypted
with GPG before touching the disk.

## What is not protected

- **The filename.** `2026-04-20.dn.gpg` is visible in plaintext. An observer
  with filesystem access can see which dates have encrypted notes and their
  approximate sizes, but not their content.
- **The directory structure.** `YYYY/MM/` is always visible.
- **Metadata.** File mtime reflects when the note was last written.

If date-of-activity visibility is a concern, duras is not the right tool.

---

## How `open -c` works

1. GPG decrypts the note into a temp file under `/dev/shm` (RAM-backed
   filesystem on Linux) or `$TMPDIR` if `/dev/shm` is unavailable.
2. Your editor opens the temp file.
3. On editor exit, the temp file is re-encrypted and written atomically
   to the `.dn.gpg` path.
4. The temp file is deleted unconditionally.

The plaintext is on disk only while the editor is open, and only in
`/dev/shm` when available.

## How `append -c` works

No temp file is written. The existing ciphertext is decrypted in memory,
the new line is appended in memory, and the result is re-encrypted and
written atomically. The plaintext never reaches disk.

---

## Coexistence of plain and encrypted notes

A plain `.dn` and an encrypted `.dn.gpg` may exist for the same date.
`duras show` displays the plain note and warns that an encrypted one also
exists. Use `duras -c show` to read the encrypted note.

`duras audit` flags any date where both exist as a conflict.

---

## Search and tags

`duras search` and `duras tags` skip all `.dn.gpg` files. Decrypting every
note on each search would require passphrase entry and be slow. The count
of skipped encrypted notes is printed as a warning.

---

## Export

```sh
duras export ~/backup --encrypt
```

The archive is piped directly into GPG. No plaintext `.tar.gz` is written
to disk at any point. The result is `duras-TIMESTAMP.tar.gz.gpg`.

Without `--encrypt`, the archive is plaintext and will contain any encrypted
`.dn.gpg` files in their already-encrypted form.

---

## Key management

duras does not manage keys. Use standard GPG tooling:

```sh
gpg --list-keys
gpg --export --armor you@example.com > backup.asc
```

If you lose your private key, encrypted notes are unrecoverable.

See [GPG Setup](gpg-setup.md) for initial configuration.
