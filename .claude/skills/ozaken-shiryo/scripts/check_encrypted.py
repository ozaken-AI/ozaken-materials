#!/usr/bin/env python3
"""Verify delivery files, including the exact staged blobs, contain lockbox shells.

No password or decryption is needed. Run --staged immediately before committing
or publishing, after all preview copying and other filesystem operations.
"""
from pathlib import Path
import argparse
import base64
import subprocess
import lockbox
import oz_root
from apply_cover import targets


def verify(raw):
    if not raw.startswith('<!--OZAKEN-LOCKED2-->'):
        raise ValueError('Not an encrypted delivery shell')
    match = lockbox.VARS_RE.search(raw)
    if match is None:
        raise ValueError('Lockbox variables missing')
    if len(base64.b64decode(match['ct'], validate=True)) < 16:
        raise ValueError('Ciphertext missing')
    if any(marker in raw for marker in ('data-oz-lecture="', '<style id="oz-lecture-body-style">',
                                        '<style id="oz-cover-style">')):
        raise ValueError('Decrypted design markup found in a delivery file')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--staged', action='store_true')
    args = ap.parse_args()
    root = Path(oz_root.root(str(Path(__file__).resolve().parent)))
    paths = targets(root) + [root / 'template.html']
    for path in paths:
        rel = str(path.relative_to(root))
        raw = (subprocess.check_output(['git','show',':'+rel], cwd=root, text=True)
               if args.staged else path.read_text())
        try:
            verify(raw)
        except ValueError as error:
            raise SystemExit(f'{rel}: {error}')
    print(f'{len(paths)} {"staged" if args.staged else "working-tree"} delivery files: encrypted shells verified')


if __name__ == '__main__':
    main()
