#!/usr/bin/env python3
"""Apply the approved lecture layout without changing any existing content.

Unlike rebuilding old generators, this adds removable attributes, CSS and a
decorative script to the current page. Removing those additions must recover
the complete original document byte for byte, including SVGs and all scripts.
--input-dir permits offline QA of a private decrypted baseline. --update reads
the current encrypted files again and refuses a stale baseline before writing.
"""
from pathlib import Path
import argparse
import getpass
import hashlib
import json
import os
import re

from apply_cover import Tree, targets, safe_preview

HERE = Path(__file__).resolve().parent
SOURCES = HERE.parent / 'sources'
ASSETS = SOURCES / 'lecture_body'
STYLE = re.compile(r'<style id="oz-lecture-body-style">[\s\S]*?</style>\n')
SCRIPT = re.compile(r'<script id="oz-lecture-body-script">[\s\S]*?</script>\n')
ATTR = re.compile(r' data-oz-(?:lecture|layout|page|tone)="[^"]*"')
GUARD = "/* OZ-LECTURE-BODY guard */if(document.body.hasAttribute('data-oz-lecture'))return;/* /OZ-LECTURE-BODY guard */"
NETWORK = re.compile(r'(<script>\s*/\* パーティクル・ネットワーク背景[^<]*?\(function\(\)\{)')


def strip(source):
    """Only remove our exact, bounded additions. Do not consume nearby whitespace."""
    source = STYLE.sub('', source)
    source = SCRIPT.sub('', source)
    source = source.replace(GUARD, '')
    # Work on tags, never on quoted examples, text, CSS or script strings.
    edits = []
    for n in Tree(source).root.walk():
        if any(k in n.attrs for k in ('data-oz-lecture','data-oz-layout','data-oz-page','data-oz-tone')):
            tag = source[n.start:n.opening_end]
            edits.append((n.start, n.opening_end, ATTR.sub('', tag)))
    for a,b,value in sorted(edits, reverse=True):
        source = source[:a] + value + source[b:]
    return source


def patch(source):
    if 'tl-hero' in source and 'tl-body' in source:
        return source  # The catalogue is the design reference, with its own builder.
    source = strip(source)
    tree = Tree(source).root
    body = tree.first(tag='body')
    if body is None:
        raise ValueError('A complete HTML document is required')
    pages = [n for n in body.walk() if n.tag == 'section' and not n.has('hero')]
    if body.has('delegation-pilot'):
        layout = 'pilot'  # Preserve the already approved bespoke figures and spacing.
    elif tree.first('poster'):
        layout = 'poster'
        pages = [tree.first('poster')]
    elif any(n.has('panel') for n in pages):
        layout = 'dashboard'
    elif any(n.has('light') for n in pages):
        layout = 'editorial'
    else:
        layout = 'standard'
    if not pages:
        raise ValueError('No recognized content surface')
    additions = [(body.opening_end - 1, f' data-oz-lecture="1" data-oz-layout="{layout}"')]
    for i, page in enumerate(pages, 1):
        dark = layout == 'dashboard' or page.has('sec-navy') or page.has('sec-deep') or page.attrs.get('data-net') == 'dark'
        additions.append((page.opening_end - 1, f' data-oz-page="{i}" data-oz-tone="{"dark" if dark else "light"}"'))
    for pos, attrs in sorted(additions, reverse=True):
        source = source[:pos] + attrs + source[pos:]
    # Avoid allocating the obsolete full-chapter canvas; the original script stays recoverable.
    source = NETWORK.sub(lambda m: m[0] + GUARD, source)
    if layout == 'pilot':
        # Its A4 page margins and diagram transforms must not inherit generic rules.
        css = js = '/* OZ-LECTURE-BODY v1: approved pilot retains its complete layout and motion */'
    else:
        css = (SOURCES / 'lecture_effects.css').read_text() + '\n' + (ASSETS / 'body.css').read_text()
        js = (ASSETS / 'body.js').read_text()
    source = source.replace('</head>', '<style id="oz-lecture-body-style">\n' + css + '\n</style>\n</head>', 1)
    return source.replace('</body>', '<script id="oz-lecture-body-script">\n' + js + '\n</script>\n</body>', 1)


def validate(old, new):
    assert strip(old) == strip(new), 'Existing document changed outside the owned design additions'
    assert patch(new) == new, 'Body migration is not idempotent'
    assert new.count('<style id="oz-lecture-body-style">') == 1, 'Body styles missing or duplicated'
    assert new.count('<script id="oz-lecture-body-script">') == 1, 'Body script missing or duplicated'
    # Byte equality above covers all text, numbers, links, sources, media, SVG geometry,
    # original script behavior, hidden commands, quizzes and QR payloads.
    return {'content_sha256':hashlib.sha256(strip(old).encode()).hexdigest(),
            'pages':sum('data-oz-page' in n.attrs for n in Tree(new).root.walk())}


def main():
    import lockbox, oz_root, check_blocks
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--preview-dir', required=True, type=Path)
    ap.add_argument('--input-dir', type=Path)
    ap.add_argument('--update', action='store_true')
    args = ap.parse_args()
    root = Path(oz_root.root(str(HERE))).resolve()
    pw = None
    if args.update or not args.input_dir:
        pw = os.environ.get('OZAKEN_PW') or getpass.getpass('Master password: ')
    before = check_blocks.survey(pw) if args.update else None
    pending, report = [], []
    for path in targets(root):
        rel = path.relative_to(root)
        raw = path.read_text()
        if 'OZAKEN-LOCKED2' not in raw:
            raise ValueError('Expected encrypted material: ' + str(rel))
        old = (args.input_dir / rel).read_text() if args.input_dir else lockbox.decrypt(path, pw)
        if args.update and args.input_dir and lockbox.decrypt(path, pw) != old:
            raise ValueError('Baseline is stale; recheck current content: ' + str(rel))
        new = patch(old)
        proof = validate(old, new)
        dest = args.preview_dir / rel
        safe_preview(dest, root)
        dest.write_text(new)
        pending.append((path, new, lockbox.parse(raw).group('w')))
        report.append({'path':str(rel), **proof})
    # All documents validate before any encrypted output is modified.
    for path, new, wrappers in pending:
        if args.update:
            lockbox.encrypt(path, pw, new)
            assert lockbox.parse(path.read_text()).group('w') == wrappers, 'A wrapped key changed'
            assert lockbox.decrypt(path, pw) == new, 'Encryption round trip failed'
    if args.update:
        after = check_blocks.survey(pw)
        for rel, old in before.items():
            assert rel in after and set(old['blocks']) <= set(after[rel]['blocks']), rel
            assert after[rel]['chars'] >= old['chars'], rel
    result = {'materials':len(pending),'updated':args.update,'unchanged_content':True,'documents':report}
    (args.preview_dir / 'body-report.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f'{len(pending)} materials: original content recovered byte for byte; idempotence verified'
          + ('; encrypted outputs verified; wrapped keys and blocks preserved' if args.update else '; previews ready'))


if __name__ == '__main__':
    main()
