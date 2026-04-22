#!/usr/bin/env python3
#
# duras — daily notes as plain text files, with search and optional encryption.
# a-Shell variant: confidential notes use PGPy instead of gpg.
#
# Copyright (c) 2026 Sergiy Duras
# SPDX-License-Identifier: ISC
#

import argparse
import datetime
import io
import os
import re
import shlex
import subprocess
import sys
import tarfile
import tempfile
import types
from typing import Any, NoReturn, Optional

G = "\033[92m"
R = "\033[91m"
X = "\033[0m"

if "imghdr" not in sys.modules:
    _m = types.ModuleType("imghdr")
    _m.what = lambda file, h=None: None
    sys.modules["imghdr"] = _m
    del _m

VERSION = "1.0.7"

DEFAULT_NOTES_DIR = os.path.join(os.path.expanduser("~"), "Documents", "Notes")
DEFAULT_BACKUPS_DIR = os.path.join(
    os.path.expanduser("~"), "Documents", "Backups"
)

NOTE_EXT = ".dn"
ENC_EXT = ".dn.gpg"
DATE_FMT = "%Y-%m-%d"
DATETIME_FMT = "%Y-%m-%d %H:%M"


def notes_dir() -> str:
    d = os.environ.get("DURAS_DIR", DEFAULT_NOTES_DIR)
    return os.path.abspath(os.path.expanduser(d))


def editor() -> list[str]:
    ed = os.environ.get("EDITOR") or "vi"
    return shlex.split(ed)


def gpg_key() -> str:
    v = os.environ.get("DURAS_GPG_KEY", "")
    if not v:
        return ""
    return os.path.normpath(os.path.expanduser(os.path.expandvars(v)))


def note_path(date: datetime.date, confidential: bool = False) -> str:
    ext = ENC_EXT if confidential else NOTE_EXT
    d = notes_dir()
    return os.path.join(
        d,
        f"{date.year:04d}",
        f"{date.month:02d}",
        f"{date.strftime(DATE_FMT)}{ext}",
    )


def parse_date(s: str) -> datetime.date:
    try:
        return datetime.datetime.strptime(s, DATE_FMT).date()
    except ValueError:
        die(f"invalid date '{s}' — expected YYYY-MM-DD")


def today() -> datetime.date:
    return datetime.date.today()


def atomic_write(path: str, content: str) -> None:
    dir_ = os.path.dirname(path)
    os.makedirs(dir_, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=dir_, prefix=".duras-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def atomic_write_bytes(path: str, data: bytes) -> None:
    dir_ = os.path.dirname(path)
    os.makedirs(dir_, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=dir_, prefix=".duras-")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def note_header(date: datetime.date, is_today: bool = True) -> str:
    now = datetime.datetime.now()
    if is_today:
        return f"{date.strftime(DATE_FMT)}\n{now.strftime('%H:%M')}\n\n"
    return (
        f"{date.strftime(DATE_FMT)}\ncreated: {now.strftime(DATETIME_FMT)}\n\n"
    )


def ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def init_note(path: str, date: datetime.date, is_today: bool = True) -> None:
    atomic_write(path, note_header(date, is_today))


def append_text(path: str, text: str) -> None:
    now = datetime.datetime.now().strftime(DATETIME_FMT)
    line = f"[{now}] {text}\n"
    existing = ""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            existing = f.read()
    if existing and not existing.endswith("\n"):
        existing += "\n"
    atomic_write(path, existing + line)
    print(f"{G}ok{X}")


def open_in_editor(path: str, extra_args: Optional[list[str]] = None) -> None:
    args = editor() + (extra_args or []) + [path]
    try:
        result = subprocess.run(args)
    except FileNotFoundError:
        die(f"editor not found: {args[0]!r} — set $EDITOR")
    if result.returncode != 0:
        die(f"editor exited with status {result.returncode}")


def _pgpy_load_key() -> Any:
    try:
        import pgpy
    except ImportError:
        die("pgpy not installed — run: pip install pgpy")
    path = gpg_key()
    if not path:
        die("DURAS_GPG_KEY not set")
    try:
        key, _ = pgpy.PGPKey.from_file(path)
        return key
    except Exception as e:
        die(f"cannot load PGP key: {e}")


def _pgpy_passphrase() -> str:
    pw = os.environ.get("DURAS_GPG_PASS")
    return pw if pw is not None else input("Key passphrase: ")


def gpg_encrypt_blob(plaintext: bytes) -> str:
    import pgpy

    key = _pgpy_load_key()
    pub = key if key.is_public else key.pubkey
    msg = pgpy.PGPMessage.new(plaintext)
    return str(pub.encrypt(msg)) + "\n"


def gpg_encrypt(plaintext: bytes, dest: str) -> None:
    atomic_write(dest, gpg_encrypt_blob(plaintext))


def gpg_decrypt(path: str) -> bytes:
    try:
        import pgpy
        from pgpy.errors import PGPDecryptionError
    except ImportError:
        die("pgpy not installed")

    key = _pgpy_load_key()
    with open(path, encoding="utf-8") as f:
        msg = pgpy.PGPMessage.from_blob(f.read())
    try:
        if key.is_protected:
            with key.unlock(_pgpy_passphrase()):
                result = key.decrypt(msg).message
        else:
            result = key.decrypt(msg).message
    except PGPDecryptionError:
        die("decryption failed: wrong passphrase")

    return (
        bytes(result)
        if isinstance(result, (bytes, bytearray))
        else result.encode("utf-8")
    )


def open_confidential_in_editor(
    enc_path: str,
    date: datetime.date,
    extra_args: Optional[list[str]] = None,
    is_today: bool = True,
) -> None:
    tmp_dir = tempfile.mkdtemp(prefix="duras-")
    tmp_path = os.path.join(tmp_dir, f"{date.strftime(DATE_FMT)}.dn")
    try:
        plaintext = (
            gpg_decrypt(enc_path)
            if os.path.exists(enc_path)
            else note_header(date, is_today).encode("utf-8")
        )
        with open(tmp_path, "wb") as f:
            f.write(plaintext)
        os.chmod(tmp_path, 0o600)
        open_in_editor(tmp_path, extra_args)
        with open(tmp_path, "rb") as f:
            new_plaintext = f.read()
        ensure_dir(enc_path)
        gpg_encrypt(new_plaintext, enc_path)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        try:
            os.rmdir(tmp_dir)
        except OSError:
            pass


def cmd_open(
    date: datetime.date, confidential: bool, extra_args: list[str]
) -> None:
    t = today()
    if date > t:
        die(f"cannot open future date: {date}")
    if confidential:
        enc_path = note_path(date, confidential=True)
        ensure_dir(enc_path)
        open_confidential_in_editor(
            enc_path, date, extra_args or None, date == t
        )
    else:
        path = note_path(date)
        ensure_dir(path)
        is_new = not os.path.exists(path)
        if is_new:
            init_note(path, date, date == t)
        open_in_editor(path, extra_args or (["+4"] if is_new else []))


def cmd_append(date: datetime.date, text: str) -> None:
    t = today()
    if date > t:
        die(f"cannot append to future date: {date}")
    path = note_path(date)
    ensure_dir(path)
    if not os.path.exists(path):
        init_note(path, date, date == t)
    append_text(path, text)


def cmd_show(date: datetime.date, confidential: bool = False) -> None:
    plain, enc = note_path(date), note_path(date, confidential=True)
    if confidential:
        if os.path.exists(enc):
            sys.stdout.buffer.write(gpg_decrypt(enc))
        else:
            die("encrypted note missing")
    else:
        if os.path.exists(plain):
            with open(plain, encoding="utf-8", errors="replace") as f:
                sys.stdout.write(f.read())
        elif os.path.exists(enc):
            die("note is encrypted; use -c")
        else:
            die(f"no note for {date}")


def cmd_list(count: int) -> None:
    files = all_note_files()
    if not files:
        print("no notes found")
        return
    shown = files[-count:] if count > 0 else files
    for path in reversed(shown):
        fname = os.path.basename(path)
        date_str = fname[:10]
        size = os.path.getsize(path)
        enc = "⚿" if fname.endswith(".gpg") else " "
        print(f"· {date_str} {size/1024:>5.1f}KB {enc}")


def cmd_search(keyword: str, ignore_case: bool = False) -> None:
    rx = re.compile(re.escape(keyword), re.IGNORECASE if ignore_case else 0)
    skipped = 0
    found: bool = False
    for path in all_note_files():
        if path.endswith(".gpg"):
            skipped += 1
            continue
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                matches = [
                    (i, l.strip()) for i, l in enumerate(f, 1) if rx.search(l)
                ]
                if matches:
                    found = True
                    print(path)
                    for i, l in matches:
                        print(f"  {i}: {l}")
        except OSError as e:
            warn(f"cannot read {path}: {e}")
    if skipped:
        warn(f"{skipped} encrypted notes skipped")
    if not found:
        print(f"no matches for '{keyword}'")


def cmd_tags(tag: str = "") -> None:
    tag_rx = re.compile(r"#([A-Za-z0-9_-]+)")
    all_files = all_note_files()
    files = [f for f in all_files if not f.endswith(".gpg")]
    skipped = len(all_files) - len(files)

    if tag:
        needle = tag.lstrip("#").lower()
        found: bool = False
        for path in files:
            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    if any(
                        m.group(1).lower() == needle
                        for l in f
                        for m in tag_rx.finditer(l)
                    ):
                        print(path)
                        found = True
            except OSError as e:
                warn(f"cannot read {path}: {e}")
        if not found:
            print(f"no notes tagged #{needle}")
    else:
        tags: dict[str, int] = {}
        for path in files:
            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    for line in f:
                        for m in tag_rx.finditer(line):
                            t = m.group(1).lower()
                            tags[t] = tags.get(t, 0) + 1
            except OSError as e:
                warn(f"cannot read {path}: {e}")
        if tags:
            w = max(len(t) for t in tags)
            for t, c in sorted(tags.items()):
                print(f"#{t:<{w}}  {c}")
        else:
            print("no tags found")
    if skipped:
        warn(f"{skipped} encrypted notes skipped")


def cmd_export(confidential: bool) -> None:
    src = notes_dir()
    if not os.path.exists(src):
        die("notes directory missing")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    ext = ".tar.gz.gpg" if confidential else ".tar.gz"
    dest_path = os.path.join(DEFAULT_BACKUPS_DIR, f"duras-export-{stamp}{ext}")
    ensure_dir(dest_path)

    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        tar.add(src, arcname="Notes")

    archive_bytes = buf.getvalue()
    if confidential:
        print("Encrypting archive...")
        atomic_write(dest_path, gpg_encrypt_blob(archive_bytes))
    else:
        atomic_write_bytes(dest_path, archive_bytes)
    print(f"{G}Exported: {dest_path}{X}")


def cmd_path(date: datetime.date, confidential: bool) -> None:
    print(note_path(date, confidential))


def cmd_dir() -> None:
    print(notes_dir())


def cmd_today() -> None:
    print(today().strftime(DATE_FMT))


def all_note_files() -> list[str]:
    d = notes_dir()
    found: list[str] = []
    if not os.path.isdir(d):
        return found
    for root, _, files in os.walk(d):
        for name in files:
            if name.endswith(NOTE_EXT) or name.endswith(ENC_EXT):
                found.append(os.path.join(root, name))
    found.sort(key=os.path.basename)
    return found


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="duras",
        description="plain-text daily notes with optional encryption",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Commands:
  (none)       Open today
  open [D]     Edit note (extra args after --)
  append TXT   Quick capture to today
  show [D]     Print to stdout
  list [-n N]  List recent
  search KW    Search plain notes
  tags [TAG]   List tags
  export       Archive to .tar.gz
  path/dir/today/help

Options:
  -c, --confidential  Use PGP (open, show, path, export)
  -d, --date DATE      Set date (YYYY-MM-DD)
""",
    )
    p.add_argument("--version", action="version", version=f"duras {VERSION}")
    p.add_argument("-c", "--confidential", action="store_true")
    sub = p.add_subparsers(dest="cmd")

    p_open = sub.add_parser("open")
    p_open.add_argument("date", nargs="?")
    p_open.add_argument("extra", nargs=argparse.REMAINDER)

    p_app = sub.add_parser("append")
    p_app.add_argument("-d", "--date", dest="date")
    p_app.add_argument("text")

    p_show = sub.add_parser("show")
    p_show.add_argument("date", nargs="?")

    p_list = sub.add_parser("list")
    p_list.add_argument("-n", "--count", type=int, default=10)

    p_search = sub.add_parser("search")
    p_search.add_argument("keyword")
    p_search.add_argument("-i", "--ignore-case", action="store_true")

    p_tags = sub.add_parser("tags")
    p_tags.add_argument("tag", nargs="?", default="")

    sub.add_parser("export")

    p_path = sub.add_parser("path")
    p_path.add_argument("date", nargs="?")

    sub.add_parser("dir")
    sub.add_parser("today")
    sub.add_parser("help")
    return p


def die(msg: str) -> NoReturn:
    print(f"duras: {msg}", file=sys.stderr)
    sys.exit(1)


def warn(msg: str) -> None:
    print(f"duras: warning: {msg}", file=sys.stderr)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    t = today()

    if args.cmd is None:
        extra = (
            sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
        )
        cmd_open(t, args.confidential, extra)
        return
    if args.cmd == "help":
        parser.print_help()
        return

    def get_date() -> datetime.date:
        return parse_date(args.date) if getattr(args, "date", None) else t

    if args.cmd == "open":
        cmd_open(
            get_date(),
            args.confidential,
            [a for a in (args.extra or []) if a != "--"],
        )
    elif args.cmd == "append":
        if args.confidential:
            die("--confidential not supported for append")
        cmd_append(get_date(), args.text)
    elif args.cmd == "show":
        cmd_show(get_date(), args.confidential)
    elif args.cmd == "list":
        cmd_list(args.count)
    elif args.cmd == "search":
        cmd_search(args.keyword, args.ignore_case)
    elif args.cmd == "tags":
        cmd_tags(args.tag)
    elif args.cmd == "export":
        cmd_export(args.confidential)
    elif args.cmd == "path":
        cmd_path(get_date(), args.confidential)
    elif args.cmd == "dir":
        cmd_dir()
    elif args.cmd == "today":
        cmd_today()


if __name__ == "__main__":
    main()
