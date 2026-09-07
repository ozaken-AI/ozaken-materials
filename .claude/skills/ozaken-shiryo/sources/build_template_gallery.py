#!/usr/bin/env python3
# coding: utf-8
"""Build only the template catalogue. --publish preserves its existing lockbox keys.

python3 build_template_gallery.py --preview /absolute/work/preview/template.html
OZAKEN_PW=... python3 build_template_gallery.py --publish

gen_template.py remains the ordinary article skeleton. Its real function calls
supply examples here. The catalogue is an always-visible reference, so article-only
section/CTA checks do not apply; shared colour/font and SVG checks still apply.
No other material, registry, profile, or shared renderer is written.
"""
from pathlib import Path
import argparse, functools, inspect, json, os, re, runpy, sys
HERE=Path(__file__).resolve().parent
SCRIPTS=HERE.parent/'scripts';sys.path.insert(0,str(SCRIPTS))
from template_gallery.catalog import CATALOG as BASE_CATALOG,CATEGORIES,BLOCKS as BASE_BLOCKS
from template_gallery.next import FIGURES as NEW_FIGURES, PARTS as NEW_PARTS, scene as new_scene, parts as new_parts, curtain
CATALOG = [*BASE_CATALOG, *NEW_FIGURES]
BLOCKS = {**BASE_BLOCKS, **NEW_PARTS}
from template_gallery.scenes import scene,e
import domain_fig,blocks,build_page
# The shared keynav module requires an environment variable at import time, even
# though its JS export never reads a key or touches encrypted files.
_keynav_preview = "OZAKEN_PW" not in os.environ
if _keynav_preview: os.environ["OZAKEN_PW"] = "template-preview"
import apply_keynav
if _keynav_preview: os.environ.pop("OZAKEN_PW")

def examples():
    figures={};parts={};originals=[]
    def wrap(mod,name,store):
        fn=getattr(mod,name);originals.append((mod,name,fn))
        signature_fn=inspect.getclosurevars(fn).nonlocals.get('fn',fn) if mod is domain_fig else fn
        @functools.wraps(fn)
        def call(*args,**kwargs):
            bound=inspect.signature(signature_fn).bind(*args,**kwargs);bound.apply_defaults()
            data=dict(bound.arguments);html=fn(*args,**kwargs)
            if mod is blocks or name in data.get('title',''):
                if name not in store: store[name]={'args':data,'html':html}
            return html
        setattr(mod,name,call)
    try:
        for item in BASE_CATALOG:wrap(domain_fig,'fig_'+item['id'],figures)
        for key in BASE_BLOCKS:wrap(blocks,key,parts)
        runpy.run_path(str(HERE/'gen_template.py'),run_name='template_examples')
    finally:
        for mod,name,fn in originals:setattr(mod,name,fn)
    assert len(figures)==30,figures.keys()
    assert len(parts)==24,parts.keys()
    return figures,parts

def mini(kind):
    # Deliberately text-free silhouettes: labels stay readable outside thumbnails.
    def rect(x,y,w,h,c=''):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" class="{c}"/>'
    def line(d,c=''):return f'<path d="{d}" class="{c}"/>'
    if kind=='cutaway':art=''.join(line(f'M35 {15+i*19} L85 {3+i*19} L154 {20+i*19} L106 {34+i*19} Z','accent' if i==1 else '') for i in range(4))
    elif kind=='rebuild':art=''.join(rect(x,y,34,19,'filled' if i<4 else '') for i,(x,y) in enumerate([(27,13),(72,13),(27,43),(72,43),(137,28),(137,60)]))+line('M119 10 V90','faint')
    elif kind=='gate':art=line('M18 50 H88 M88 20 V40 M88 60 V85 M88 50 C115 50 114 24 140 24 M88 50 C115 50 114 76 140 76')+rect(143,14,40,20)+rect(143,66,40,20,'filled')
    elif kind=='waiting':art=rect(20,20,150,20)+rect(20,61,110,20)+rect(87,20,50,20,'filled')+rect(52,61,50,20,'filled')
    elif kind=='dims':art=line('M100 10 135 30 135 68 100 88 65 68 65 30 Z M65 30 100 50 135 30 M100 50 V88')+line('M25 50 H50 M148 50 H177','faint')
    elif kind in ('cycle','issues','loop4'):
        art='<circle cx="100" cy="50" r="32"/>'+''.join(rect(x,y,22,14,'filled' if i==1 else '') for i,(x,y) in enumerate([(89,11),(123,43),(89,75),(55,43)]))
    elif kind in ('tree','kpi'):
        art=line('M100 25 V45 M45 45 H155 M45 45 V66 M100 45 V66 M155 45 V66')+rect(80,10,40,17,'filled')+''.join(rect(x,65,36,20) for x in [27,82,137])
    elif kind in ('pyramid','context'):
        art=''.join(rect(100-w/2,12+i*27,w,20,'filled' if i==0 else '') for i,w in enumerate([58,94,134]))
    elif kind=='waterline':
        art=''.join(rect(35,10+i*27,130,22) for i in range(3))+line('M25 47 Q50 37 75 47 T125 47 T175 47','accent')
    elif kind in ('bars','ranges','orgs'):
        art=''.join(rect(30,12+i*26,w,15,'filled' if i==1 else '') for i,w in enumerate([135,88,48]))+line('M25 7 V92','faint')
    elif kind=='donut':art='<circle cx="100" cy="50" r="33" stroke-width="15"/><circle cx="100" cy="50" r="33" stroke-width="15" stroke-dasharray="84 124" class="accent"/>'
    elif kind=='stack':art=''.join(rect(30+i*45,22+j*34,40,23,'filled' if i==j else '') for j in range(2) for i in range(3))
    elif kind in ('stairs','ladder','timeline'):
        art=line('M22 80 H67 V57 H112 V34 H160 V15')+''.join(rect(25+i*45,50-i*20,30,18,'filled' if i==2 else '') for i in range(3))
    elif kind in ('flow','roles','cols','stats'):
        art=line('M35 50 H165','faint')+''.join(rect(18+i*58,27,45,46,'filled' if i==1 else '') for i in range(3))
    elif kind in ('quad','map','katagata'):
        art=line('M100 8 V92 M18 50 H182','faint')+''.join(rect(x,y,55,28,'filled' if i==1 else '') for i,(x,y) in enumerate([(34,14),(112,14),(34,59),(112,59)]))
    elif kind in ('sheet','matrix','check'):
        art=''.join(rect(28+i*49,12+j*27,43,20,'filled' if i==1 and j==1 else '') for j in range(3) for i in range(3))
    else:
        art=''.join(rect(x,17+j*38,60,25,'filled' if x==114 else '') for j in range(2) for x in [26,114])+line('M90 49 H110')
    return f'<svg viewBox="0 0 200 100" class="tl-mini" aria-hidden="true">{art}</svg>'

def build():
    from template_gallery.lecture import build as lecture
    figures, parts = examples()
    html = lecture(figures, parts, CATALOG, BLOCKS, CATEGORIES, build_page.STYLE,
                   apply_keynav.JS, HERE / 'template_gallery', mini)
    errors = build_page.check_tokens(html)
    if errors: raise ValueError(errors)
    return html


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--preview',type=Path);ap.add_argument('--publish',action='store_true');args=ap.parse_args()
    page=build()
    if args.preview:
        args.preview.parent.mkdir(parents=True,exist_ok=True);args.preview.write_text(page)
        print('Preview written:',args.preview)
    if args.publish:
        import lockbox,oz_root
        pw=os.environ.get('OZAKEN_PW')
        if not pw:
            import getpass
            pw=getpass.getpass('Master password: ')
        target=Path(oz_root.root(str(HERE)))/'template.html'
        before=lockbox.parse(target.read_text()).group('w')
        lockbox.encrypt(str(target),pw,page)
        assert lockbox.parse(target.read_text()).group('w')==before
        assert lockbox.decrypt(str(target),pw)==page
        print('Updated template.html; existing keys preserved.')
    if not args.preview and not args.publish:ap.error('Choose --preview or --publish')
if __name__=='__main__':main()
