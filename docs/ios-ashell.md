# iOS / a-Shell

`duras_ashell.py` is a standalone variant for
[a-Shell mini](https://holzschu.github.io/a-Shell_iOS/) on iOS.
It uses [PGPy](https://github.com/SecurityInnovation/PGPy) for encryption
instead of system `gpg`, which is not available on iOS.

---

## Differences from standard duras

| | duras | duras_ashell |
| --- | --- | --- |
| Encryption | system `gpg` | PGPy (pure Python) |
| Key source | GPG keyring | `.asc` file path |
| Passphrase | gpg-agent | `DURAS_GPG_PASS` or prompt |
| Encrypted format | GPG binary | PGP ASCII-armored |
| `append -c` | supported | not supported |

---

## Setup

### 1. Install a-Shell mini

From the App Store: search "a-Shell mini".

### 2. Install PGPy

In a-Shell:

```sh
pip install pgpy
```

### 3. Install duras_ashell

Download `duras_ashell.py` from the
[releases page](https://codeberg.org/duras/duras/releases) and copy it
into a-Shell:

```sh
cp ~/Documents/duras_ashell.py ~/bin/duras
chmod +x ~/bin/duras
```

Verify:

```sh
duras today
```

### 4. Set up a PGP key

You need a PGP key in `.asc` (ASCII-armored) format as a file on the device.

**Option A: Export from desktop and transfer**

```sh
# on desktop
gpg --export-secret-keys --armor you@example.com > my-key.asc
```

AirDrop `my-key.asc` to Files, then move it to `~/Documents/` in a-Shell.

**Option B: Generate on device with PGPy**

```python
import pgpy, pgpy.constants as C
key = pgpy.PGPKey.new(C.PubKeyAlgorithm.EdDSA, C.EllipticCurveOID.Ed25519)
uid = pgpy.PGPUID.new("Your Name", email="you@example.com")
key.add_uid(uid,
    usage={C.KeyFlags.Sign, C.KeyFlags.EncryptCommunications},
    hash_alg=C.HashAlgorithm.SHA256,
    ciphers=[C.SymmetricKeyAlgorithm.AES256],
    compression=[C.CompressionAlgorithm.ZLIB])
with open("/root/Documents/my-key.asc", "w") as f:
    f.write(str(key))
```

Run this in a-Shell with `python3`.

### 5. Configure environment variables

Add to `~/.profile` in a-Shell:

```sh
export DURAS_DIR=~/Documents/.Notes
export DURAS_GPG_KEY=~/Documents/my-key.asc
export DURAS_GPG_PASS=your-passphrase
```

If `DURAS_GPG_PASS` is not set, duras_ashell prompts for the passphrase on
each decryption. On iOS there is no agent to cache it, so setting the env
var avoids repeated prompts.

Reload:

```sh
source ~/.profile
```

### 6. Test

```sh
duras today
duras append "first note"
duras show
```

---

## Notes directory

Use `~/Documents/.Notes` (hidden, survives app reinstall) or
`~/Documents/Notes` (visible in Files app). The directory is created
automatically on first use.

---

## Limitations

- `duras -c append` is not supported in this variant.
- Cross-tool encrypted note compatibility with system GPG is not tested.
- No `man` page; refer to this documentation.
