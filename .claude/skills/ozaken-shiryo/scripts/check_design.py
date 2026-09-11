#!/usr/bin/env python3
"""Read-only release check for omitted cover/body migrations across all materials.

--staged checks the exact Git blobs that will be committed. Passwords are entered
privately. No decrypted page or password is written to disk or printed.
--input-dir can inspect an existing private plaintext preview without a password.
This detects structural omissions; visual browser QA remains required.
"""
from pathlib import Path
import argparse
import getpass
import os
import re
import subprocess

from apply_cover import Tree, targets, text


def issues(source):
    tree = Tree(source).root
    body = tree.first(tag='body')
    found = []
    hero = tree.first('hero')
    if hero is None or hero.attrs.get('data-oz-cover') != '1':
        found.append('common cover missing')
    elif re.search('[、。]', text(hero.outer(source))):
        found.append('visible cover punctuation remains')
    for name, tag in [('oz-cover-style', 'style'), ('oz-cover-script', 'script'),
                      ('oz-lecture-body-style', 'style'), ('oz-lecture-body-script', 'script')]:
        nodes = [n for n in tree.walk() if n.tag == tag and n.attrs.get('id') == name]
        if len(nodes) != 1 or not nodes[0].inner(source).strip():
            found.append(name + ' missing, empty or duplicated')
    layout = body.attrs.get('data-oz-layout') if body else None
    if body is None or body.attrs.get('data-oz-lecture') != '1' or layout not in {'standard', 'editorial', 'dashboard', 'poster', 'pilot'}:
        found.append('lecture body layout missing or unknown')
    if body:
        pages = ([tree.first('poster')] if layout == 'poster' else
                 [n for n in body.walk() if n.tag == 'section' and not n.has('hero')])
        if not pages or any(n is None or 'data-oz-page' not in n.attrs or
                            n.attrs.get('data-oz-tone') not in {'light', 'dark'} for n in pages):
            found.append('a content surface is outside the lecture design')
    return found


def main():
    import lockbox, oz_root
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group()
    group.add_argument('--staged', action='store_true')
    group.add_argument('--input-dir', type=Path)
    args = ap.parse_args()
    root = Path(oz_root.root(str(Path(__file__).resolve().parent)))
    pw = None if args.input_dir else os.environ.get('OZAKEN_PW') or getpass.getpass('Master password: ')
    failures = 0
    paths = targets(root)
    for path in paths:
        rel = path.relative_to(root)
        if args.input_dir:
            source = (args.input_dir / rel).read_text()
        else:
            raw = (subprocess.check_output(['git', 'show', ':' + str(rel)], cwd=root, text=True)
                   if args.staged else path.read_text())
            m = lockbox.parse(raw)
            ck = lockbox.content_key(m, pw)
            source = lockbox.AESGCM(ck).decrypt(lockbox.b64d(m['ivc']), lockbox.b64d(m['ct']), None).decode('utf-8')
        errors = issues(source)
        if errors:
            failures += 1
            print(str(rel) + ': ' + '; '.join(errors), flush=True)
    print(f'{len(paths)} materials checked; {failures} design omissions')
    raise SystemExit(1 if failures else 0)


if __name__ == '__main__':
    main()
