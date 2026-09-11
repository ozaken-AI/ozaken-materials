"""Static, printable learning diagrams and a scoped update runner.

Edits current complete documents, never rebuilds unrelated chapters from old
fragments. Plaintext previews must remain outside the repository.
"""
from pathlib import Path
import argparse
from collections import Counter
import getpass
import hashlib
import json
import os
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'scripts'))
import apply_body
from apply_cover import Tree, safe_preview
from page_parts import sec, cards, srcs
from html import escape

STYLE_RE = re.compile(r'<style id="oz-practical-guide-style">[\s\S]*?</style>\n')


def figure(label, title, content, caption):
    return (f'<div class="figure pg-figure"><p class="fig-title"><span class="fig-no">{label}</span>{title}</p>'
            f'<div class="pg-canvas">{content}</div><p class="figure-cap">{caption}</p></div>')


def route(items, loop=False):
    """(short index, label, handoff). Words stay fixed; a decorative line moves."""
    cells = ''.join(f'<li><span class="pg-index">{a}</span><strong>{b}</strong><p>{c}</p></li>' for a,b,c in items)
    line = '<svg class="pg-wire" viewBox="0 0 900 12" preserveAspectRatio="none" aria-hidden="true"><path class="a-flow" d="M0 6H900" fill="none" stroke="#2e5496" stroke-width="1.5"/></svg>'
    back = '<p class="pg-return">↶　改善点を次の共同化へ戻す</p>' if loop else ''
    return f'<div class="pg-route">{line}<ol style="--pg-count:{len(items)}">{cells}</ol>{back}</div>'


def sheet(items, label='設計メモ'):
    return f'<div class="pg-sheet"><p class="pg-label">{label}</p><dl>' + ''.join(
        f'<div><dt>{a}</dt><dd>{b}</dd></div>' for a,b in items) + '</dl></div>'


def exchange(left_label, left, right_label, right):
    return (f'<div class="pg-exchange"><div><span class="pg-label">{left_label}</span><p class="pg-quote">{left}</p></div>'
            f'<span class="pg-arrow" aria-hidden="true">→</span><div><span class="pg-label">{right_label}</span><p class="pg-quote">{right}</p></div></div>')


def rows(headers, data):
    # Real table semantics + the shared decorative column hover. No content toggles.
    def cell(i, value):
        return ('<th scope="row">' + value + '</th>') if i == 0 else '<td>' + value + '</td>'
    return '<div class="pg-table-wrap"><table class="pg-table"><thead><tr>' + ''.join(
        f'<th scope="col">{v}</th>' for v in headers) + '</tr></thead><tbody>' + ''.join(
        '<tr>'+''.join(cell(i,v) for i,v in enumerate(row))+'</tr>'
        for row in data) + '</tbody></table></div>'


def chapter(key, tone, eyebrow, title, sub, fig, notes=(), after=''):
    html = sec(tone, eyebrow, title, sub, fig=fig,
               body=cards(notes) if notes else None, after=after)
    return html.replace('<section ', f'<section id="{key}" data-practical-guide="{key}" ', 1)


def sections(page):
    return [n for n in Tree(page).root.walk() if n.tag == 'section' and not n.has('hero')]


def cover_lead(page, copy):
    node = Tree(page).root.first('oz-cover-lead')
    if not node:
        raise ValueError('Common cover lead missing')
    return page[:node.opening_end] + copy + page[node.closing_start:]


def replace_chapters(page, groups):
    """groups: [(old eyebrow, new complete chapters)]. Retain related chips."""
    source = apply_body.strip(page)
    source = STYLE_RE.sub('', source)
    edits = []
    for eyebrow, built in groups:
        key = re.search(r'data-practical-guide="([^"]+)"', built)[1]
        matches = [n for n in sections(source) if n.attrs.get('data-practical-guide','').split('--')[0] == key.split('--')[0]]
        if not matches:
            matches = [n for n in sections(source) if f'>{eyebrow}<' in n.outer(source)]
        if not matches:
            raise ValueError('Cannot locate chapter: ' + eyebrow)
        # A generated group must be adjacent. Never swallow an unowned chapter.
        all_nodes = sections(source)
        positions = [all_nodes.index(n) for n in matches]
        assert positions == list(range(positions[0], positions[-1]+1))
        chips = ''.join(n.outer(source) for node in matches for n in node.walk() if n.has('xr-chips'))
        if chips:
            built = built.replace('  </div>\n</section>', chips + '\n  </div>\n</section>', 1)
        edits.append((matches[0].start, matches[-1].end, built.rstrip()))
    for a,b,built in sorted(edits, reverse=True):
        source = source[:a] + built + source[b:]
    source = apply_body.patch(source)
    css = (HERE / 'practical_guides.css').read_text()
    return source.replace('</head>', f'<style id="oz-practical-guide-style">\n{css}\n</style>\n</head>', 1)


def validate(before, after, transform):
    assert transform(after) == after, 'Revision must be idempotent'
    a,b = apply_body.strip(before), apply_body.strip(after)
    ta,tb = Tree(a).root,Tree(b).root
    cover_same = ta.first('hero').outer(a) == tb.first('hero').outer(b)
    if getattr(transform,'cover_copy',None):
        normalized = cover_lead(a,transform.cover_copy)
        assert Tree(normalized).root.first('hero').outer(normalized) == tb.first('hero').outer(b), 'Cover changed outside approved lead'
    else:
        assert cover_same, 'Cover changed'
    scripts = lambda s: re.findall(r'<script\b[^>]*>[\s\S]*?</script>', s)
    assert scripts(a) == scripts(b), 'Existing script changed'
    links = lambda t: Counter(n.attrs.get('href') for n in t.walk() if n.tag == 'a')
    assert not links(ta) - links(tb), 'Existing link removed'
    # Chapters untouched by the revision remain byte-identical, including figures.
    unchanged = [n.outer(a) for n in sections(a) if n.outer(a) in b]
    return {'cover_unchanged':cover_same,'cover_layout_unchanged':True,'scripts_unchanged':True,'links_preserved':True,
            'unchanged_chapters':len(unchanged),'chapters':len(sections(b)),
            'revised_chapters':sum('data-practical-guide' in n.attrs for n in sections(b)),
            'before_sha256':hashlib.sha256(before.encode()).hexdigest(),
            'after_sha256':hashlib.sha256(after.encode()).hexdigest()}


def run(transforms, description):
    import lockbox, oz_root
    ap = argparse.ArgumentParser(description=description)
    ap.add_argument('--preview-dir', type=Path, required=True)
    ap.add_argument('--input-dir', type=Path)
    ap.add_argument('--update', action='store_true')
    args = ap.parse_args()
    root = Path(oz_root.root(str(HERE))).resolve()
    pw = (os.environ.get('OZAKEN_PW') or getpass.getpass('Master password: ')) if args.update or not args.input_dir else None
    pending, report = [], []
    for rel, transform in transforms.items():
        path = root / rel
        old = (args.input_dir / rel).read_text() if args.input_dir else lockbox.decrypt(path, pw)
        if args.update and args.input_dir:
            assert lockbox.decrypt(path,pw) == old, 'Stale baseline: '+rel
        new = transform(old)
        proof = validate(old,new,transform)
        dest = args.preview_dir / rel
        safe_preview(dest,root)
        dest.write_text(new)
        pending.append((path,new,lockbox.parse(path.read_text()).group('w')))
        report.append({'path':rel,**proof})
    for path,new,w in pending:
        if args.update:
            lockbox.encrypt(path,pw,new)
            assert lockbox.parse(path.read_text()).group('w') == w
            assert lockbox.decrypt(path,pw) == new
    report_path = args.preview_dir / ('seci-report.json' if len(transforms)==1 else 'levels-report.json')
    safe_preview(report_path,root)
    report_path.write_text(json.dumps({'updated':args.update,'documents':report},ensure_ascii=False,indent=2))
    print(f'{len(pending)} documents verified; '+('encrypted outputs updated' if args.update else 'private previews ready'))
