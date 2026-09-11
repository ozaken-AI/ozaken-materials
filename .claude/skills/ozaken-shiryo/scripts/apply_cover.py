#!/usr/bin/env python3
"""Adopt the approved lecture cover without regenerating or rewriting the body.

Run --preview-dir outside the repository to inspect every material. --update
also writes encrypted outputs, retaining the existing lockbox envelope and W.
The same patch() is the last step of publish.compose and the pilot builder.
"""
from pathlib import Path
from html.parser import HTMLParser
from dataclasses import dataclass, field
import argparse
from collections import Counter
import getpass
import html
import json
import os
import re
import sys
import unicodedata

HERE = Path(__file__).resolve().parent
SOURCES = HERE.parent / 'sources'
sys.path.insert(0, str(SOURCES))
from lecture_cover import cover_air, curtain
ASSETS = SOURCES / 'lecture_cover'
STYLE_RE = re.compile(r'<style id="oz-cover-style">[\s\S]*?</style>\s*')
SCRIPT_RE = re.compile(r'<script id="oz-cover-script">[\s\S]*?</script>\s*')
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


@dataclass
class Node:
    tag: str
    attrs: dict
    start: int
    opening_end: int
    end: int = 0
    closing_start: int = 0
    children: list = field(default_factory=list)

    def has(self, cls):
        return cls in (self.attrs.get('class') or '').split()

    def walk(self):
        yield self
        for child in self.children:
            yield from child.walk()

    def first(self, *classes, tag=None):
        return next((n for n in self.walk() if (not tag or n.tag == tag)
                     and (not classes or any(n.has(c) for c in classes))), None)

    def outer(self, source):
        return source[self.start:self.end]

    def inner(self, source):
        return source[self.opening_end:self.closing_start]


class Tree(HTMLParser):
    """Record source ranges; never serialize the unaffected document through a DOM."""
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.lines = [0]
        self.lines.extend(m.end() for m in re.finditer('\n', source))
        self.root = Node('root', {}, 0, 0, len(source), len(source))
        self.stack = [self.root]
        self.feed(source)

    def position(self):
        row, col = self.getpos()
        return self.lines[row - 1] + col

    def handle_starttag(self, tag, attrs):
        start = self.position()
        node = Node(tag, dict(attrs), start, start + len(self.get_starttag_text()))
        self.stack[-1].children.append(node)
        if tag in VOID:
            node.end = node.closing_start = node.opening_end
        else:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            node = self.stack.pop()
            node.end = node.closing_start = node.opening_end

    def handle_endtag(self, tag):
        index = next((i for i in range(len(self.stack)-1, 0, -1) if self.stack[i].tag == tag), None)
        if index is not None:
            start = self.position()
            end = self.source.index('>', start) + 1
            for node in self.stack[index:]:
                node.closing_start, node.end = start, end
            del self.stack[index:]


def text(fragment, breaks=False):
    fragment = re.sub(r'<(?:script|style)\b[\s\S]*?</(?:script|style)>', '', fragment)
    if breaks:
        fragment = re.sub(r'<br\s*/?>', '\x00', fragment)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', '', fragment))).strip()


def words(fragment, sentences=False):
    """Only visible copy is normalized; attributes, links, scripts and body stay intact."""
    value = text(fragment, breaks=True).replace('、', '')
    value = value.replace('。', '\x00' if sentences else '')
    return '<br>'.join(html.escape(p.strip()) for p in value.split('\x00') if p.strip())


def clean_inline(fragment):
    # Metadata may contain spans, strong emphasis, dates and links. Keep their markup.
    return re.sub(r'(?<=>)[^<]+', lambda m: m[0].replace('、', '').replace('。', ''),
                  '>' + fragment)[1:]


def cover(title, lead, meta, eyebrow, home, start_link='', footer='', cover_id=''):
    lines = words(title).split('<br>')
    width = max(sum(1 if unicodedata.east_asian_width(c) in 'WF' else .5
                    for c in html.unescape(line)) for line in lines)
    scale = min(5.5, 84 / max(width, 1))
    maximum = min(86, round(1280 * scale / 100))
    identity = ' id="' + html.escape(cover_id, quote=True) + '"' if cover_id else ''
    title_markup = '<br>'.join('<span class="oz-cover-line">' + line + '</span>' for line in lines)
    return (f'<section class="hero" data-oz-cover="1"{identity} style="--cover-scale:{scale:.3f}vw;--cover-max:{maximum}px;--cover-compact:{min(maximum,64)}px">'
            + cover_air() + '<a class="oz-cover-back" href="' + html.escape(home, quote=True) + '">← AI資料アーカイブに戻る</a>'
            + '<div class="oz-cover-copy"><span class="oz-cover-eyebrow">' + words(eyebrow) + '</span>'
            + '<h1 class="hero-title oz-cover-title">' + title_markup + '</h1>'
            + ('<p class="hero-copy oz-cover-lead">' + words(lead, sentences=True) + '</p>' if lead else '')
            + ('<div class="oz-cover-meta">' + clean_inline(meta) + '</div>' if meta else '')
            + start_link + '</div><div class="oz-cover-art" aria-hidden="true">' + curtain() + '</div>'
            + '<div class="oz-cover-footer">' + (clean_inline(footer) or '<span>OZAKEN / MATERIALS</span>') + '</div></section>')


def migrate(source):
    tree = Tree(source).root
    hero = next((n for n in tree.walk() if n.tag == 'section' and n.has('hero')), None)
    if hero is not None:
        if 'data-oz-cover' in hero.attrs:
            return source
        title = hero.first(tag='h1')
        if title is None:
            raise ValueError('A cover without a title requires an explicit adapter')
        lead = hero.first('hero-sub', 'sub') or hero.first('hero-copy')
        meta = hero.first('hero-meta', 'byline')
        eyebrow = hero.first('eyebrow') or hero.first('hero-tag')
        home = hero.first('oz-home')
        link = hero.first('dp-start')
        foot = hero.first('dp-cover-foot')
        selected = [n for n in (title, lead, meta, eyebrow, home, link, foot) if n]
        extras = []
        extra_classes = {'hero-rail', 'stats', 'hero-stats', 'phase-stats', 'phase-scale', 'hero-tags', 'hero-cat', 'hero-tag', 'hero-copy'}
        for node in hero.walk():
            if node in selected or any(parent.start <= node.start < parent.end for parent in extras + selected):
                continue
            if any(node.has(cls) for cls in extra_classes):
                extras.append(node)
        # Unknown meaningful content must be handled explicitly, never silently dropped.
        covered = selected + extras + [n for n in hero.walk() if n.has('texture') or n.has('hero-glyph') or n.has('hero-ghost') or n.has('hero-scroll') or n.attrs.get('aria-hidden') == 'true']
        remainder = hero.inner(source)
        for node in sorted(covered, key=lambda n: n.start, reverse=True):
            # Work on a copy with fixed offsets, replacing the whole range by spaces.
            a, b = node.start - hero.opening_end, node.end - hero.opening_end
            remainder = remainder[:a] + ' ' * (b-a) + remainder[b:]
        if text(remainder):
            raise ValueError('Unmapped cover content: ' + text(remainder)[:120])
        start_link = ('<a class="oz-cover-link" href="' + html.escape(link.attrs['href'], quote=True) + '">' + words(link.inner(source)) + '</a>') if link else ''
        new = cover(title.inner(source), lead.inner(source) if lead else '', meta.inner(source) if meta else '',
                    eyebrow.inner(source) if eyebrow else 'OZAKEN / MATERIALS',
                    home.attrs['href'] if home else '/index.html', start_link,
                    foot.inner(source) if foot else '', hero.attrs.get('id', ''))
        if extras:
            new += '<div class="oz-cover-details">' + ''.join(n.outer(source) for n in sorted(extras, key=lambda n:n.start)) + '</div>'
        body = tree.first(tag='body')
        redundant = [n for n in body.children if n.has('oz-homebar') and n.start < hero.start]
        mastheads = [n for n in body.children if n.tag == 'header' and n.attrs.get('id') == 'hdr' and n.start < hero.start]
        new += ''.join(n.outer(source) for n in mastheads)
        edits = [(hero.start, hero.end, new)] + [(n.start, n.end, '') for n in redundant + mastheads]
        for a, b, replacement in sorted(edits, reverse=True):
            source = source[:a] + replacement + source[b:]
        return source
    # Two materials are an at-a-glance poster and a statistics board, not slide decks.
    # Their facts, legends and data remain below the new cover, byte for byte.
    poster = tree.first('poster')
    board = tree.first('h-sub')
    if poster:
        old = poster.first('top-l')
        title = old.first(tag='h1'); lead = old.first(tag='p'); eyebrow = old.first('eyebrow')
    elif board:
        old = tree.first('top').children[0]
        title = old.first(tag='h1'); lead = board; eyebrow = old.first('badge')
    else:
        raise ValueError('No recognized material cover')
    new = cover(title.inner(source), lead.inner(source), '', eyebrow.inner(source), '/index.html')
    if board and not poster:
        new = new.replace('data-oz-cover="1"', 'data-oz-cover="1" data-cover-board', 1)
    body = tree.first(tag='body')
    # Remove only the old heading block and redundant archive strip.
    remove = [old] + [n for n in body.children if n.has('oz-homebar')]
    for node in sorted(remove, key=lambda n:n.start, reverse=True):
        source = source[:node.start] + source[node.end:]
    return source[:body.opening_end] + new + source[body.opening_end:]


def patch(source):
    if 'tl-hero' in source and 'tl-body' in source:
        return source  # The catalogue uses the same decoration and its own reference layout.
    source = migrate(source)
    # Disable the obsolete generated HUD and canvas before they can be mounted.
    source = source.replace("if (!hero || hero.querySelector('.oz-sweep')) return;",
                            "if (!hero || hero.hasAttribute('data-oz-cover') || hero.querySelector('.oz-sweep')) return;")
    source = STYLE_RE.sub('', source)
    source = SCRIPT_RE.sub('', source)
    styles = (ASSETS / 'motion.css').read_text() + '\n' + (ASSETS / 'cover.css').read_text()
    source = source.replace('</head>', '<style id="oz-cover-style">\n' + styles + '\n</style>\n</head>')
    return source.replace('</body>', '<script id="oz-cover-script">\n' + (ASSETS / 'cover.js').read_text() + '\n</script>\n</body>')


def targets(root):
    import oz_root
    folders = sorted(p for p in root.glob('[0-9][0-9]_*') if p.is_dir())
    folders += [root / d for d in oz_root.BACKSTAGE_DIRS]
    return sorted(p for folder in folders for p in folder.glob('*.html'))


def safe_preview(path, root):
    # Preview trees often contain links back to encrypted output files.
    if path.is_symlink() or root in path.resolve().parents:
        raise ValueError('Preview must be a real file outside the repository: ' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)


def validate(old, new):
    """Check the unencrypted result before an archive-wide write, without logging copy."""
    a, b = Tree(old).root, Tree(new).root
    assert patch(new) == new, 'Cover migration is not idempotent'
    hero = b.first('hero')
    assert hero and 'data-oz-cover' in hero.attrs, 'Common cover missing'
    assert not re.search('[、。]', text(hero.outer(new))), 'Cover punctuation remains'
    sections = lambda tree, source: [n.outer(source) for n in tree.walk()
                                    if n.tag == 'section' and not n.has('hero')]
    assert sections(a, old) == sections(b, new), 'A body section changed'
    links = lambda tree: Counter(n.attrs.get('href') for n in tree.walk() if n.tag == 'a')
    missing = links(a) - links(b)
    missing.pop('/index.html', None)  # The duplicate cover archive strip is consolidated.
    assert not missing, 'An existing content link disappeared'
    scripts = lambda source: [s for s in re.findall(r'<script[^>]*>[\s\S]*?</script>', source)
                              if 'id="oz-cover-script"' not in s]
    guarded = old.replace("if (!hero || hero.querySelector('.oz-sweep')) return;",
                          "if (!hero || hero.hasAttribute('data-oz-cover') || hero.querySelector('.oz-sweep')) return;")
    assert scripts(guarded) == scripts(new), 'An existing command or content script changed'


def main():
    import lockbox, oz_root, check_blocks
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--preview-dir', required=True, type=Path)
    ap.add_argument('--input-dir', type=Path, help='Read an existing private decrypted baseline')
    ap.add_argument('--only', nargs='+', metavar='PATH', help='Limit the refresh to these repository-relative materials')
    ap.add_argument('--update', action='store_true')
    args = ap.parse_args()
    root = Path(oz_root.root(str(HERE))).resolve()
    selected = targets(root)
    if args.only:
        requested = {Path(p).as_posix() for p in args.only}
        available = {p.relative_to(root).as_posix() for p in selected}
        if requested - available:
            ap.error('Unknown material path(s): ' + ', '.join(sorted(requested - available)))
        selected = [p for p in selected if p.relative_to(root).as_posix() in requested]
    pw = None
    if args.update or not args.input_dir:
        pw = os.environ.get('OZAKEN_PW') or getpass.getpass('Master password: ')
    before = check_blocks.survey(pw) if args.update else None
    pending = []
    for path in selected:
        raw = path.read_text()
        if 'OZAKEN-LOCKED2' not in raw:
            raise ValueError('Expected encrypted material: ' + str(path))
        old = (args.input_dir / path.relative_to(root)).read_text() if args.input_dir else lockbox.decrypt(path, pw)
        if args.update and args.input_dir and lockbox.decrypt(path, pw) != old:
            raise ValueError('Baseline is stale; recheck current content: ' + str(path.relative_to(root)))
        new = patch(old)
        validate(old, new)
        dest = args.preview_dir / path.relative_to(root)
        safe_preview(dest, root)
        dest.write_text(new)
        pending.append((path, new, lockbox.parse(raw).group('w')))
    # All transforms must validate before any repository output is changed.
    for path, new, wrappers in pending:
        if args.update:
            lockbox.encrypt(path, pw, new)
            assert lockbox.parse(path.read_text()).group('w') == wrappers
            assert lockbox.decrypt(path, pw) == new
    if args.update:
        after = check_blocks.survey(pw)
        for rel, old in before.items():
            assert rel in after and set(old['blocks']) <= set(after[rel]['blocks']), rel
            assert after[rel]['chars'] >= old['chars'] * .9, rel
    report = {'materials': len(pending), 'updated': args.update, 'paths': [str(p.relative_to(root)) for p,_,_ in pending]}
    report_path = args.preview_dir / 'cover-report.json'
    safe_preview(report_path, root)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f'{len(pending)} material covers: preview ready' + ('; encrypted outputs verified; blocks preserved' if args.update else ''))


if __name__ == '__main__':
    main()
