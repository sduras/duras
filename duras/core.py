#!/usr/bin/env python3
#
# duras — daily notes as plain text files, with search and optional encryption.
# core library: all domain logic. Imported by cli.py.
#
# Copyright (c) 2026 Sergiy Duras
# SPDX-License-Identifier: ISC

import datetime
import io
import os
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
from typing import Optional

VERSION = "1.0.0"

DEFAULT_NOTES_DIR = os.path.join(os.path.expanduser("~"), "Documents", "Notes")
NOTE_EXT = ".dn"
ENC_EXT = ".dn.gpg"
DATE_FMT = "%Y-%m-%d"
DATETIME_FMT = "%Y-%m-%d %H:%M"


class DurasError(Exception):
    """Raised by core on any recoverable user-facing error."""

    exit_code = 1


class DurasNotFoundError(DurasError):
    """Note or directory not found. exit_code=2."""

    exit_code = 2


class DurasInputError(DurasError):
    """Invalid user input (bad date, wrong flag, etc.). exit_code=3."""

    exit_code = 3


class DurasExternalError(DurasError):
    """External tool failure (gpg, editor). exit_code=4."""

    exit_code = 4


def warn(msg: str) -> None:
    print(f"duras: warning: {msg}", file=sys.stderr)


def notes_dir() -> str:
    d = os.environ.get("DURAS_DIR", DEFAULT_NOTES_DIR)
    return os.path.abspath(os.path.expanduser(d))


def editor() -> list[str]:
    ed = os.environ.get("EDITOR")
    if ed:
        return shlex.split(ed)

    for candidate in ("nano", "vi", "ed"):
        if shutil.which(candidate):
            return [candidate]

    raise DurasExternalError("no editor found: set $EDITOR")


def gpg_key() -> str:
    return os.environ.get("DURAS_GPG_KEY") or ""


def today() -> datetime.date:
    return datetime.date.today()


def parse_date(s: str) -> datetime.date:
    try:
        return datetime.datetime.strptime(s, DATE_FMT).date()
    except ValueError:
        pass
    try:
        return today() + datetime.timedelta(days=int(s))
    except ValueError:
        raise DurasInputError(
            f"invalid date '{s}' — expected YYYY-MM-DD or integer offset (e.g. -1, 0, 7)"
        )


def note_path(date: datetime.date, confidential: bool = False) -> str:
    ext = ENC_EXT if confidential else NOTE_EXT
    d = notes_dir()
    return os.path.join(
        d,
        f"{date.year:04d}",
        f"{date.month:02d}",
        f"{date.strftime(DATE_FMT)}{ext}",
    )


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


def _is_broken_symlink(entry: "os.DirEntry[str]") -> bool:
    return entry.is_symlink() and not os.path.exists(entry.path)


def _parse_note_filename(
    name: str,
) -> tuple[Optional[datetime.date], str]:
    if name.endswith(ENC_EXT):
        stem = name[: -len(ENC_EXT)]
    elif name.endswith(NOTE_EXT):
        stem = name[: -len(NOTE_EXT)]
    else:
        return None, "not a .dn or .dn.gpg file"
    try:
        return datetime.datetime.strptime(stem, DATE_FMT).date(), ""
    except ValueError:
        return None, f"filename date {stem!r} is not a valid YYYY-MM-DD date"


def _header_lines(date: datetime.date, is_today: bool) -> int:
    return 3


def ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def _ensure_notes_dir_perms() -> None:
    d = notes_dir()
    try:
        os.makedirs(d, exist_ok=True)
        mode = os.stat(d).st_mode & 0o777
        if mode & 0o077:
            os.chmod(d, 0o700)
    except OSError:
        pass


def _secure_tmpdir() -> str:
    shm = "/dev/shm"
    if os.path.isdir(shm) and os.access(shm, os.W_OK):
        try:
            return tempfile.mkdtemp(dir=shm, prefix="duras-")
        except OSError:
            pass
    return tempfile.mkdtemp(prefix="duras-")


def atomic_write(path: str, content: str) -> None:
    dir_ = os.path.dirname(path)
    os.makedirs(dir_, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=dir_, prefix=".duras-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
        dir_fd = os.open(dir_, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
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
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
        dir_fd = os.open(dir_, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
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


def init_note(path: str, date: datetime.date, is_today: bool = True) -> None:
    atomic_write(path, note_header(date, is_today))


def append_text(path: str, text: str) -> None:
    now = datetime.datetime.now().strftime(DATETIME_FMT)
    line = f"[{now}] {text}\n"
    existing = ""
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8", errors="strict") as f:
                existing = f.read()
        except UnicodeDecodeError as e:
            raise DurasError(
                f"note is not valid UTF-8, will not append: {path}: {e}"
            )
    if existing and not existing.endswith("\n"):
        existing += "\n"
    atomic_write(path, existing + line)


def open_in_editor(path: str, extra_args: Optional[list[str]] = None) -> None:
    args = editor() + (extra_args or []) + [path]
    try:
        result = subprocess.run(args)
    except FileNotFoundError:
        raise DurasExternalError(
            f"editor not found: {args[0]!r} — set $EDITOR"
        )
    if result.returncode != 0:
        raise DurasExternalError(
            f"editor exited with status {result.returncode}"
        )


def gpg_encrypt(plaintext: bytes, dest: str) -> None:
    key = gpg_key()
    dir_ = os.path.dirname(dest) or "."
    os.makedirs(dir_, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=dir_, prefix=".duras-")
    try:
        os.close(fd)
        cmd = ["gpg", "--batch", "--yes", "--quiet", "--output", tmp]
        if key:
            cmd += ["--recipient", key, "--encrypt"]
        else:
            cmd += ["--default-recipient-self", "--encrypt"]
        result = subprocess.run(cmd, input=plaintext, capture_output=True)
        if result.returncode != 0:
            raise DurasExternalError(
                f"gpg encryption failed: {result.stderr.decode(errors='replace').strip()}"
            )
        os.chmod(tmp, 0o600)
        os.replace(tmp, dest)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def gpg_decrypt(path: str) -> bytes:
    result = subprocess.run(
        ["gpg", "--batch", "--quiet", "--decrypt", path],
        capture_output=True,
    )
    if result.returncode != 0:
        raise DurasExternalError(
            f"gpg decryption failed: {result.stderr.decode(errors='replace').strip()}"
        )
    return result.stdout


def open_confidential_in_editor(
    enc_path: str,
    date: datetime.date,
    extra_args: Optional[list[str]] = None,
    is_today: bool = True,
) -> None:
    tmp_dir = _secure_tmpdir()
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
    is_today = date == today()
    if date > today():
        raise DurasInputError(
            f"cannot open a note for a future date: {date.strftime(DATE_FMT)}"
        )
    if confidential:
        enc_path = note_path(date, confidential=True)
        ensure_dir(enc_path)
        open_confidential_in_editor(enc_path, date, extra_args, is_today)
    else:
        path = note_path(date)
        ensure_dir(path)
        is_new = not os.path.exists(path)
        if is_new:
            init_note(path, date, is_today)
        ea = extra_args or (
            ["+" + str(_header_lines(date, is_today) + 1)] if is_new else []
        )
        open_in_editor(path, ea)


def cmd_append_confidential(date: datetime.date, text: str) -> None:
    enc_path = note_path(date, confidential=True)
    is_today = date == today()
    now = datetime.datetime.now().strftime(DATETIME_FMT)
    line = f"[{now}] {text}\n"
    if os.path.exists(enc_path):
        existing = gpg_decrypt(enc_path).decode("utf-8", errors="replace")
        if existing and not existing.endswith("\n"):
            existing += "\n"
        new_content = existing + line
    else:
        ensure_dir(enc_path)
        new_content = note_header(date, is_today) + line
    gpg_encrypt(new_content.encode("utf-8"), enc_path)


def cmd_append(
    date: datetime.date, text: str, confidential: bool = False
) -> None:
    if date > today():
        raise DurasInputError(
            f"cannot append to a future date: {date.strftime(DATE_FMT)}"
        )
    if confidential:
        cmd_append_confidential(date, text)
        return
    is_today = date == today()
    path = note_path(date)
    ensure_dir(path)
    if not os.path.exists(path):
        init_note(path, date, is_today)
    append_text(path, text)


def cmd_show(date: datetime.date, confidential: bool = False) -> None:
    plain = note_path(date)
    enc = note_path(date, confidential=True)
    plain_exists = os.path.exists(plain)
    enc_exists = os.path.exists(enc)
    if confidential:
        if enc_exists:
            data = gpg_decrypt(enc)
            sys.stdout.buffer.write(data)
        elif plain_exists:
            raise DurasInputError(
                f"no encrypted note for {date.strftime(DATE_FMT)} (plain note exists; omit -c)"
            )
        else:
            raise DurasNotFoundError(f"no note for {date.strftime(DATE_FMT)}")
    else:
        if plain_exists:
            if enc_exists:
                warn(
                    "both plain and encrypted notes exist for this date; showing plain (use -c for encrypted)"
                )
            try:
                with open(plain, encoding="utf-8", errors="strict") as f:
                    sys.stdout.write(f.read())
            except UnicodeDecodeError as e:
                raise DurasError(f"note is not valid UTF-8: {plain}: {e}")
        elif enc_exists:
            raise DurasInputError(
                "only encrypted note exists for this date; use -c to decrypt"
            )
        else:
            raise DurasNotFoundError(f"no note for {date.strftime(DATE_FMT)}")


def cmd_list(count: int) -> None:
    files = all_note_files()
    if not files:
        print("no notes found")
        return
    shown = files[-count:] if count > 0 else files
    for path in reversed(shown):
        size = os.path.getsize(path)
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
        name = os.path.basename(path)
        enc = " ⚿" if path.endswith(".gpg") else ""
        print(
            f"· {mtime.strftime('%Y-%m-%d %H:%M')} {size/1024:>5.1f}KB  {name}{enc}"
        )


def cmd_search(keyword: str, ignore_case: bool = False) -> None:
    flags = re.IGNORECASE if ignore_case else 0
    rx = re.compile(re.escape(keyword), flags)
    skipped = 0
    found = False
    for path in all_note_files():
        if path.endswith(".gpg"):
            skipped += 1
            continue
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                file_matches: list[tuple[int, str]] = []
                for lineno, line in enumerate(f, 1):
                    if rx.search(line):
                        file_matches.append((lineno, line.rstrip()))
        except OSError as e:
            warn(f"cannot read {path}: {e}")
            continue
        if file_matches:
            found = True
            print(path)
            for lineno, line in file_matches:
                print(f"  {lineno}: {line}")
    if skipped:
        warn(f"{skipped} encrypted note(s) not searched")
    if not found:
        print(f"no matches for '{keyword}'")


def cmd_tags(tag: str = "") -> None:
    tag_rx = re.compile(r"#([A-Za-z0-9_-]+)")
    if tag:
        needle = tag.lstrip("#").lower()
        skipped = 0
        found = False
        for path in all_note_files():
            if path.endswith(".gpg"):
                skipped += 1
                continue
            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    for line in f:
                        if any(
                            m.group(1).lower() == needle
                            for m in tag_rx.finditer(line)
                        ):
                            print(path)
                            found = True
                            break
            except OSError as e:
                warn(f"cannot read {path}: {e}")
        if skipped:
            warn(f"{skipped} encrypted note(s) not searched")
        if not found:
            print(f"no notes tagged #{needle}")
        return
    tags: dict[str, int] = {}
    skipped = 0
    for path in all_note_files():
        if path.endswith(".gpg"):
            skipped += 1
            continue
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                for line in f:
                    for m in tag_rx.finditer(line):
                        t = m.group(1).lower()
                        tags[t] = tags.get(t, 0) + 1
        except OSError as e:
            warn(f"cannot read {path}: {e}")
    if skipped:
        warn(f"{skipped} encrypted note(s) not searched")
    if not tags:
        print("no tags found")
        return
    width = max(len(t) for t in tags)
    for t, count in sorted(tags.items()):
        print(f"#{t:<{width}}  {count}")


def cmd_stats() -> None:
    files = all_note_files()
    if not files:
        print("no notes found")
        return
    total_size = sum(os.path.getsize(p) for p in files)
    plain = [p for p in files if not p.endswith(".gpg")]
    enc = [p for p in files if p.endswith(".gpg")]
    date_rx = re.compile(r"(\d{4}-\d{2}-\d{2})\.dn")
    dates: set[datetime.date] = set()
    for p in files:
        m = date_rx.search(os.path.basename(p))
        if m:
            try:
                dates.add(datetime.date.fromisoformat(m.group(1)))
            except ValueError:
                pass
    streak = 0
    if dates:
        check = today()
        while check in dates:
            streak += 1
            check -= datetime.timedelta(days=1)
    oldest = min(dates).isoformat() if dates else "—"
    newest = max(dates).isoformat() if dates else "—"
    print(
        f"notes:   {len(plain)} plain, {len(enc)} encrypted ({len(files)} total)"
    )
    print(f"size:    {total_size / 1024:.1f} KB")
    print(f"range:   {oldest} — {newest}")
    print(f"streak:  {streak} day(s)")


def cmd_export(dest_dir: str, encrypt: bool) -> None:
    d = notes_dir()
    if not os.path.isdir(d):
        raise DurasNotFoundError(f"notes directory not found: {d}")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    try:
        os.makedirs(dest_dir, exist_ok=True)
    except OSError as e:
        raise DurasError(f"cannot create destination directory: {e}")

    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        tar.add(d, arcname="notes")
    archive_bytes = buf.getvalue()
    buf.close()

    if encrypt:
        dest = os.path.join(dest_dir, f"duras-{stamp}.tar.gz.gpg")
        dir_ = os.path.dirname(os.path.abspath(dest))
        fd, tmp = tempfile.mkstemp(dir=dir_, prefix=".duras-export-")
        try:
            os.close(fd)
            key = gpg_key()
            cmd = ["gpg", "--batch", "--yes", "--quiet", "--output", tmp]
            if key:
                cmd += ["--recipient", key, "--encrypt"]
            else:
                cmd += ["--default-recipient-self", "--encrypt"]
            result = subprocess.run(
                cmd, input=archive_bytes, capture_output=True
            )
            if result.returncode != 0:
                raise DurasExternalError(
                    f"gpg encryption of archive failed: {result.stderr.decode(errors='replace').strip()}"
                )
            os.chmod(tmp, 0o600)
            os.replace(tmp, dest)
        except DurasError:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
        except Exception as e:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise DurasError(f"export failed: {e}")
    else:
        dest = os.path.join(dest_dir, f"duras-{stamp}.tar.gz")
        dir_ = os.path.dirname(os.path.abspath(dest))
        fd, tmp = tempfile.mkstemp(dir=dir_, prefix=".duras-export-")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(archive_bytes)
            os.chmod(tmp, 0o600)
            os.replace(tmp, dest)
        except Exception as e:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise DurasError(f"export failed: {e}")

    print(dest)


def cmd_path(date: datetime.date, confidential: bool) -> None:
    print(note_path(date, confidential))


def cmd_dir() -> None:
    print(notes_dir())


def cmd_today() -> None:
    print(today().strftime(DATE_FMT))


def cmd_audit() -> int:
    d = notes_dir()
    if not os.path.isdir(d):
        print("notes directory does not exist; nothing to audit")
        return 0

    issues: list[str] = []
    seen_plain: set[datetime.date] = set()
    seen_enc: set[datetime.date] = set()

    try:
        root_entries = sorted(os.scandir(d), key=lambda e: e.name)
    except OSError as e:
        raise DurasError(f"cannot read notes directory: {e}")

    for year_entry in root_entries:
        if _is_broken_symlink(year_entry):
            issues.append(f"broken symlink: {year_entry.path}")
            continue
        if not year_entry.is_dir(follow_symlinks=False):
            issues.append(f"unexpected file at notes root: {year_entry.path}")
            continue
        if not re.fullmatch(r"\d{4}", year_entry.name):
            issues.append(
                f"unexpected directory at notes root: {year_entry.path}"
            )
            continue
        year = int(year_entry.name)

        try:
            month_entries = sorted(
                os.scandir(year_entry.path), key=lambda e: e.name
            )
        except OSError as e:
            raise DurasError(f"cannot read directory: {e}")

        for month_entry in month_entries:
            if _is_broken_symlink(month_entry):
                issues.append(f"broken symlink: {month_entry.path}")
                continue
            if not month_entry.is_dir(follow_symlinks=False):
                issues.append(
                    f"unexpected file in year directory: {month_entry.path}"
                )
                continue
            if not re.fullmatch(r"\d{2}", month_entry.name):
                issues.append(
                    f"unexpected directory in year directory: {month_entry.path}"
                )
                continue
            month = int(month_entry.name)
            if not 1 <= month <= 12:
                issues.append(f"invalid month directory: {month_entry.path}")
                continue

            try:
                file_entries = sorted(
                    os.scandir(month_entry.path), key=lambda e: e.name
                )
            except OSError as e:
                raise DurasError(f"cannot read directory: {e}")

            for file_entry in file_entries:
                if _is_broken_symlink(file_entry):
                    issues.append(f"broken symlink: {file_entry.path}")
                    continue
                if file_entry.is_dir(follow_symlinks=False):
                    issues.append(
                        f"unexpected directory in month directory: {file_entry.path}"
                    )
                    continue
                date, err = _parse_note_filename(file_entry.name)
                if err:
                    issues.append(
                        f"unexpected file: {file_entry.path} ({err})"
                    )
                    continue
                assert date is not None
                if date.year != year or date.month != month:
                    issues.append(
                        f"path mismatch: {file_entry.path}"
                        f" (filename date {date} does not match"
                        f" path {year}/{month:02d})"
                    )
                if date > today():
                    issues.append(f"future date: {file_entry.path}")
                if file_entry.name.endswith(ENC_EXT):
                    seen_enc.add(date)
                else:
                    seen_plain.add(date)

    for conflict_date in sorted(seen_plain & seen_enc):
        issues.append(
            f"conflicting notes for {conflict_date.isoformat()}:"
            f" both .dn and .dn.gpg exist"
        )

    for issue in issues:
        print(issue)

    if issues:
        print(f"\n{len(issues)} issue(s) found")
    else:
        print("collection is clean")

    return len(issues)


def cmd_echo(date: datetime.date) -> None:
    target_md = (date.month, date.day)
    matches: list[str] = []
    for path in all_note_files():
        parsed, err = _parse_note_filename(os.path.basename(path))
        if err or parsed is None:
            continue
        if (parsed.month, parsed.day) == target_md:
            matches.append(path)
    matches.sort(key=lambda p: os.path.basename(p), reverse=True)
    if not matches:
        print(f"no notes for {date.strftime('%m-%d')} in any year")
        return
    for path in matches:
        print(path)


def cmd_near(date: datetime.date) -> None:
    for offset in range(-3, 4):
        candidate = date + datetime.timedelta(days=offset)
        for confidential in (False, True):
            path = note_path(candidate, confidential=confidential)
            if os.path.exists(path):
                print(path)


def _parse_date_strict(s: str) -> datetime.date:
    try:
        return datetime.datetime.strptime(s, DATE_FMT).date()
    except ValueError:
        raise DurasInputError(
            f"invalid date '{s}' — duras mv requires YYYY-MM-DD"
        )


def cmd_mv(old_date: datetime.date, new_date: datetime.date) -> None:
    if old_date == new_date:
        raise DurasInputError("source and destination dates are the same")

    old_plain = note_path(old_date)
    old_enc = note_path(old_date, confidential=True)
    new_plain = note_path(new_date)
    new_enc = note_path(new_date, confidential=True)

    has_plain = os.path.exists(old_plain)
    has_enc = os.path.exists(old_enc)

    if not has_plain and not has_enc:
        raise DurasNotFoundError(f"no note for {old_date.strftime(DATE_FMT)}")
    if os.path.exists(new_plain) or os.path.exists(new_enc):
        raise DurasInputError(
            f"target date {new_date.strftime(DATE_FMT)} already has a note"
        )

    if has_plain:
        ensure_dir(new_plain)
    if has_enc:
        ensure_dir(new_enc)

    if has_plain:
        os.replace(old_plain, new_plain)
    if has_enc:
        os.replace(old_enc, new_enc)

    old_month_dir = os.path.dirname(old_plain)
    old_year_dir = os.path.dirname(old_month_dir)
    for dir_ in (old_month_dir, old_year_dir):
        try:
            os.rmdir(dir_)
        except OSError:
            pass
