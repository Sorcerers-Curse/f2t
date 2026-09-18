# f2t

`f2t` builds a text tree diagram from a filesystem directory.

It is the counterpart to [`t2f`]([[https://example.com/t2f]](https://github.com/Sorcerers-Curse/t2f)), which creates files and directories from a text tree.

## Features

- Recursively walks a directory and prints a tree using standard box-drawing characters.
- Directories are listed before files; entries are sorted alphabetically (case-insensitive).
- Supports ignoring files/directories by glob patterns.
- Can limit traversal depth.
- Can output only directories (`--no-files`).
- Can override the root name (`--root-name`).
- Can emit mojibake box-drawing characters (`--mojibake`) for compatibility with legacy files.
- Output is compatible with `t2f` input format.

## Requirements

- Python 3.8+
- No third-party dependencies

## Usage

```bash
python f2t.py /path/to/directory
python f2t.py /path/to/directory -o tree.txt
python f2t.py /path/to/directory --no-files
python f2t.py /path/to/directory --max-depth 2
python f2t.py /path/to/directory --ignore "*.pyc" --ignore "__pycache__"
python f2t.py /path/to/directory --mojibake
