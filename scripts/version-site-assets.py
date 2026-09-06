#!/usr/bin/env python3
"""Version local CSS, JavaScript, and profile configuration URLs in index.html.

Run after editing assets and before publishing:
    python3 scripts/version-site-assets.py
Use --check in validation to fail when the HTML references stale content hashes.
External URLs and inline script/style contents are left untouched.
"""

import argparse
import hashlib
import html
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import parse_qsl, unquote, urlencode, urlsplit, urlunsplit


ATTRIBUTE = re.compile(r'''([^\s/>=]+)(?:\s*=\s*("[^"]*"|'[^']*'|[^\s>]+))?''')


def replace_attribute(tag, name, value):
    """Change one attribute value without reserializing the surrounding HTML."""
    encoded = '"' + html.escape(value, quote=True) + '"'
    start = re.match(r'<\s*[\w:-]+', tag).end()
    for match in ATTRIBUTE.finditer(tag, start):
        if match.group(1).lower() != name:
            continue
        if match.group(2) is None:
            return tag[:match.end()] + '=' + encoded + tag[match.end():]
        return tag[:match.start(2)] + encoded + tag[match.end(2):]
    end = tag.rfind('/>') if tag.rstrip().endswith('/>') else tag.rfind('>')
    return tag[:end].rstrip() + ' ' + name + '=' + encoded + tag[end:]


def version_url(value, root, html_path):
    url = urlsplit(value)
    if url.scheme or url.netloc or not url.path:
        return value
    path = unquote(url.path)
    asset = ((root / path.lstrip('/')) if path.startswith('/') else (html_path.parent / path)).resolve()
    if not asset.is_relative_to(root):
        raise ValueError('Asset path is outside the site root: ' + value)
    if not asset.is_file():
        raise ValueError('Local asset is missing: ' + value)
    digest = hashlib.sha256(asset.read_bytes()).hexdigest()
    query = [(key, item) for key, item in parse_qsl(url.query, keep_blank_values=True) if key != 'v']
    query.append(('v', digest))
    return urlunsplit((url.scheme, url.netloc, url.path, urlencode(query), url.fragment))


class AssetParser(HTMLParser):
    def __init__(self, source, root, html_path):
        super().__init__(convert_charrefs=False)
        self.root, self.html_path = root, html_path
        self.offsets, self.replacements = [0], []
        for match in re.finditer('\n', source):
            self.offsets.append(match.end())

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        attribute = 'href' if tag == 'link' else 'src' if tag == 'script' else None
        if not attribute or not values.get(attribute):
            return
        value = values[attribute]
        url = urlsplit(value)
        if url.scheme or url.netloc:
            return
        suffix = Path(unquote(url.path)).suffix.lower()
        if (tag == 'link' and suffix != '.css') or (tag == 'script' and suffix not in ('.js', '.mjs')):
            return
        original = self.get_starttag_text()
        updated = replace_attribute(original, attribute, version_url(value, self.root, self.html_path))
        config = values.get('data-profile-config')
        if tag == 'script' and Path(url.path).name == 'profile-media.js' and config is None:
            config = str(Path(url.path).with_suffix('.json'))
        if config:
            updated = replace_attribute(updated, 'data-profile-config', version_url(config, self.root, self.html_path))
        if updated != original:
            line, column = self.getpos()
            start = self.offsets[line - 1] + column
            self.replacements.append((start, start + len(original), updated))

    handle_startendtag = handle_starttag


def version_html(source, root, html_path):
    root, html_path = Path(root).resolve(), Path(html_path).resolve()
    parser = AssetParser(source, root, html_path)
    parser.feed(source)
    parser.close()
    for start, end, value in reversed(parser.replacements):
        source = source[:start] + value + source[end:]
    return source, len(parser.replacements)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1], help='Site root directory')
    parser.add_argument('--html', type=Path, default=Path('index.html'), help='HTML path relative to the site root')
    parser.add_argument('--check', action='store_true', help='Report stale versions without editing')
    args = parser.parse_args()
    root = args.root.resolve()
    html_path = args.html.resolve() if args.html.is_absolute() else (root / args.html).resolve()
    try:
        original = html_path.read_text(encoding='utf-8')
        updated, count = version_html(original, root, html_path)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if count and args.check:
        print(f'{html_path.name}: {count} asset tag(s) need updated content versions.')
        return 1
    if count:
        html_path.write_text(updated, encoding='utf-8')
    print(f'{html_path.name}: {count} asset tag(s) updated.' if count else f'{html_path.name}: asset versions are current.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
