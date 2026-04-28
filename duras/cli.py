#!/usr/bin/env python3
#
# duras — daily notes as plain text files, with search and optional encryption.
# No external dependencies (GnuPG optional for confidential notes).
#
# Copyright (c) 2026 Sergiy Duras
# SPDX-License-Identifier: ISC

import argparse
import sys

from .core import (
    VERSION,
    DurasError,
    DurasExternalError,
    DurasInputError,
    DurasNotFoundError,
    _ensure_notes_dir_perms,
    _parse_date_strict,
    cmd_append,
    cmd_audit,
    cmd_dir,
    cmd_echo,
    cmd_export,
    cmd_list,
    cmd_mv,
    cmd_near,
    cmd_open,
    cmd_path,
    cmd_search,
    cmd_show,
    cmd_stats,
    cmd_tags,
    cmd_today,
    parse_date,
    today,
)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="duras",
        description="plain-text daily notes with optional encryption",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
SUBCOMMANDS
  open [DATE] [-- ARGS]   Open note in $EDITOR; pass ARGS after --
  append [-d DATE] [TEXT] Append timestamped line; omit TEXT to read stdin
  show [DATE]             Print note to stdout
  list [-n N]             List recent notes (default: 10, 0 = all)
  search KEYWORD [-i]     Search plain notes (literal, -i = ignore case)
  tags [TAG]              List all #tags or notes containing #TAG
  stats                   Show counts, size, date range, streak
  export [DIR] [--encrypt] Archive notes to tar.gz (optionally GPG)
  path [DATE]             Print absolute note path
  dir                     Print notes root directory
  today                   Print today's date (YYYY-MM-DD)
  audit                   Validate notes directory structure
  echo [DATE]             List notes sharing the same MM-DD across years
  near [DATE]             List notes within ±3 days of a date
  mv FROM TO              Move a note from one date to another (YYYY-MM-DD only)

DATE FORMATS
  YYYY-MM-DD              Absolute date (e.g. 2026-01-15)
  INTEGER                 Relative offset: 0 (today), -1 (yesterday)

ENVIRONMENT
  DURAS_DIR               Notes directory (default: ~/Documents/Notes)
  EDITOR                  Editor (fallback: nano, vi, ed)
  DURAS_GPG_KEY           GPG recipient (default: self)

COMMON WORKFLOWS
  duras                    Open today's note
  duras open -1            Open yesterday's note
  duras open -- +10        Open note and jump to line 10 in editor

  duras append "note"      Append to today
  duras append -d -1 "x"  Append to yesterday
  cat file.txt | duras append   Append stdin
  cmd | duras append            Pipe directly into today's note

  duras -c open            Open encrypted note
  duras -c append "secret" Append encrypted entry
  duras show -c            Show encrypted note

  duras list               Show recent notes
  duras list -n 0          Show all notes

  duras search "error"     Search notes
  duras search "todo" -i   Case-insensitive search

  duras tags               List all tags
  duras tags project       Notes with #project

  duras export ~/backup            Create archive
  duras export ~/backup --encrypt  Encrypted archive

  duras audit              Verify notes directory is structurally clean

  duras echo               List past notes on today's date in history
  duras echo 2026-03-15    List past notes on March 15 across all years
  duras near               List notes within ±3 days of today
  duras near 2026-01-01    List notes around a specific date

  duras mv 2026-04-17 2026-04-16   Move a misdated note (YYYY-MM-DD only)

NOTE FORMAT
  Files are plain text (.dn); encrypted notes use .dn.gpg
  Header:  date: YYYY-MM-DD
  Entries: YYYY-MM-DD HH:MM  text
  Encrypted notes are skipped by search and tags

EXIT CODES
  0  Success
  1  Generic error
  2  Not found
  3  Invalid input
  4  External tool failure

Documentation:
  https://duras.readthedocs.io/en/latest/
  https://codeberg.org/duras/duras
""",
    )
    p.add_argument("--version", action="version", version=f"duras {VERSION}")
    p.add_argument(
        "-c",
        "--confidential",
        action="store_true",
        help="use gpg encryption for this note",
    )

    sub = p.add_subparsers(dest="cmd")

    p_open = sub.add_parser("open", help="open note in $EDITOR")
    p_open.add_argument(
        "date", nargs="?", help="YYYY-MM-DD or offset (default: 0)"
    )
    p_open.add_argument(
        "extra",
        nargs=argparse.REMAINDER,
        help="args passed to $EDITOR (after --)",
    )

    p_app = sub.add_parser("append", help="append text without editor")
    p_app.add_argument(
        "-d", "--date", dest="date", help="YYYY-MM-DD or offset (default: 0)"
    )
    p_app.add_argument(
        "text",
        nargs="?",
        default=None,
        help="text to append; omit to read from stdin",
    )

    p_show = sub.add_parser("show", help="print note to stdout")
    p_show.add_argument(
        "date", nargs="?", help="YYYY-MM-DD or offset (default: 0)"
    )

    p_list = sub.add_parser("list", help="list recent notes")
    p_list.add_argument(
        "-n",
        "--count",
        type=int,
        default=10,
        metavar="N",
        help="notes to show (0 = all)",
    )

    p_search = sub.add_parser("search", help="search notes for keyword")
    p_search.add_argument("keyword", help="text to search for")
    p_search.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        help="case-insensitive search",
    )

    p_tags = sub.add_parser("tags", help="list all #tags (or notes for a tag)")
    p_tags.add_argument(
        "tag", nargs="?", default="", help="#TAG to filter by (optional)"
    )

    sub.add_parser("stats", help="show note counts, size, and streak")

    p_export = sub.add_parser("export", help="archive notes to tar.gz")
    p_export.add_argument(
        "dest",
        nargs="?",
        default=".",
        help="destination directory (default: .)",
    )
    p_export.add_argument(
        "--encrypt", action="store_true", help="encrypt the archive with gpg"
    )

    p_path = sub.add_parser("path", help="print note file path")
    p_path.add_argument(
        "date", nargs="?", help="YYYY-MM-DD or offset (default: 0)"
    )

    sub.add_parser("dir", help="print notes directory")
    sub.add_parser("today", help="print today's date")
    sub.add_parser("audit", help="validate notes directory structure")

    p_echo = sub.add_parser(
        "echo", help="list notes sharing the same MM-DD across years"
    )
    p_echo.add_argument(
        "date", nargs="?", help="YYYY-MM-DD or offset (default: today)"
    )

    p_near = sub.add_parser("near", help="list notes within ±3 days of a date")
    p_near.add_argument(
        "date", nargs="?", help="YYYY-MM-DD or offset (default: today)"
    )

    p_mv = sub.add_parser("mv", help="move a note from one date to another")
    p_mv.add_argument(
        "old_date", metavar="FROM", help="source date (YYYY-MM-DD)"
    )
    p_mv.add_argument(
        "new_date", metavar="TO", help="destination date (YYYY-MM-DD)"
    )

    return p


def main() -> None:
    argv = sys.argv[1:]

    parser = build_parser()
    args = parser.parse_args(argv)
    confidential = args.confidential

    _ensure_notes_dir_perms()

    try:
        if args.cmd is None:
            extra_args = []
            if "--" in argv:
                split = argv.index("--")
                extra_args = argv[split + 1 :]
            cmd_open(today(), confidential, extra_args)

        elif args.cmd == "open":
            date = parse_date(args.date) if args.date else today()
            ea = [a for a in (args.extra or []) if a != "--"]
            cmd_open(date, confidential, ea)

        elif args.cmd == "append":
            date = parse_date(args.date) if args.date else today()
            if args.text is None or args.text == "-":
                if sys.stdin.isatty():
                    raise DurasInputError(
                        "no text given and stdin is a terminal"
                    )
                text = sys.stdin.read().rstrip("\n")
                if not text:
                    raise DurasInputError("no text read from stdin")
            else:
                text = args.text
            cmd_append(date, text, confidential)

        elif args.cmd == "show":
            date = parse_date(args.date) if args.date else today()
            cmd_show(date, confidential)

        elif args.cmd == "list":
            cmd_list(args.count)

        elif args.cmd == "search":
            cmd_search(args.keyword, args.ignore_case)

        elif args.cmd == "tags":
            cmd_tags(args.tag)

        elif args.cmd == "stats":
            cmd_stats()

        elif args.cmd == "export":
            cmd_export(args.dest, args.encrypt)

        elif args.cmd == "path":
            date = parse_date(args.date) if args.date else today()
            cmd_path(date, confidential)

        elif args.cmd == "dir":
            cmd_dir()

        elif args.cmd == "today":
            cmd_today()

        elif args.cmd == "audit":
            count = cmd_audit()
            if count:
                sys.exit(1)

        elif args.cmd == "echo":
            date = parse_date(args.date) if args.date else today()
            cmd_echo(date)

        elif args.cmd == "near":
            date = parse_date(args.date) if args.date else today()
            cmd_near(date)

        elif args.cmd == "mv":
            old_date = _parse_date_strict(args.old_date)
            new_date = _parse_date_strict(args.new_date)
            cmd_mv(old_date, new_date)

        else:
            parser.print_help()
            sys.exit(1)

    except DurasError as e:
        print(f"duras: {e}", file=sys.stderr)
        sys.exit(e.exit_code)


if __name__ == "__main__":
    main()
