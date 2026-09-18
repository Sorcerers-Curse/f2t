#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import fnmatch
from pathlib import Path
from typing import List, Optional

BRANCH_MID = '├── '
BRANCH_LAST = '└── '
PIPE = '│   '
SPACE = '    '


def should_ignore(name: str, patterns: List[str]) -> bool:
    for pat in patterns:
        if fnmatch.fnmatch(name, pat):
            return True
    return False


def sort_key(path: Path):
    return (not path.is_dir(), path.name.lower())


def walk_tree(
    directory: Path,
    prefix: str,
    lines: List[str],
    ignore_patterns: List[str],
    include_files: bool,
    max_depth: Optional[int],
    current_depth: int,
    show_root: bool,
    root_display: Optional[str] = None,
):
    if max_depth is not None and current_depth > max_depth:
        return

    try:
        entries = list(directory.iterdir())
    except PermissionError:
        lines.append(f"{prefix}{BRANCH_LAST}[permission denied]")
        return

    entries = [e for e in entries if not should_ignore(e.name, ignore_patterns)]
    entries.sort(key=sort_key)

    for i, entry in enumerate(entries):
        is_last = (i == len(entries) - 1)
        branch = BRANCH_LAST if is_last else BRANCH_MID
        connector = SPACE if is_last else PIPE

        if entry.is_dir():
            lines.append(f"{prefix}{branch}{entry.name}/")
            walk_tree(
                entry,
                prefix + connector,
                lines,
                ignore_patterns,
                include_files,
                max_depth,
                current_depth + 1,
                show_root=False,
            )
        else:
            if include_files:
                lines.append(f"{prefix}{branch}{entry.name}")


def build_tree_text(
    root: Path,
    ignore_patterns: List[str],
    include_files: bool = True,
    max_depth: Optional[int] = None,
    show_root: bool = True,
) -> str:
    if not root.is_dir():
        raise NotADirectoryError(f"{root} is not a directory")

    lines: List[str] = []

    if show_root:
        lines.append(f"{root.name}/")

    walk_tree(
        directory=root,
        prefix='',
        lines=lines,
        ignore_patterns=ignore_patterns,
        include_files=include_files,
        max_depth=max_depth,
        current_depth=0,
        show_root=show_root,
    )

    return '\n'.join(lines) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Build a text tree diagram from a filesystem directory (filesystem -> tree).'
    )
    parser.add_argument('directory', help='Root directory')
    parser.add_argument('-o', '--output', default=None,
                        help='Output file (default: stdout)')
    parser.add_argument('--no-files', action='store_true',
                        help='Show only directories, omit files')
    parser.add_argument('--max-depth', type=int, default=None,
                        help='Maximum traversal depth (0 = root only)')
    parser.add_argument('--ignore', action='append', default=[],
                        help='Ignore pattern (can be used multiple times). '
                             'Example: --ignore "*.pyc" --ignore "__pycache__"')
    parser.add_argument('--encoding', default='utf-8',
                        help='Output file encoding (default: utf-8)')
    parser.add_argument('--mojibake', action='store_true',
                        help='Output box-drawing characters in mojibake form')
    parser.add_argument('--root-name', default=None,
                        help='Override the root name in the output')
    args = parser.parse_args()

    root = Path(args.directory)
    if not root.is_dir():
        print(f"Error: {root} is not a directory.")
        return 1

    ignore_patterns = args.ignore

    try:
        text = build_tree_text(
            root=root,
            ignore_patterns=ignore_patterns,
            include_files=not args.no_files,
            max_depth=args.max_depth,
            show_root=True,
        )
    except Exception as e:
        print(f"Error while walking directory: {e}")
        return 1

    if args.root_name is not None:
        lines = text.splitlines()
        if lines:
            lines[0] = f"{args.root_name}/"
        text = '\n'.join(lines) + '\n'

    if args.mojibake:
        replacements = {
            '├': 'в”њ',
            '└': 'в””',
            '│': 'в”‚',
            '─': 'в”Ђ',
        }
        out_lines = []
        for line in text.splitlines():
            for good, bad in replacements.items():
                line = line.replace(good, bad)
            out_lines.append(line)
        text = '\n'.join(out_lines) + '\n'

    if args.output:
        Path(args.output).write_text(text, encoding=args.encoding)
        print(f"Written to {args.output}")
    else:
        print(text, end='')

    return 0


if __name__ == '__main__':
    exit(main())