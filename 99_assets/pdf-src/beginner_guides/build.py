#!/usr/bin/env python3
"""Build the three public beginner guides with selectable Japanese text.
Run: python3 99_assets/pdf-src/beginner_guides/build.py --output-root /path/to/repo
Dependencies: reportlab, fonttools, pypdf. No browser or passwords required.
"""
from __future__ import annotations
import argparse, hashlib, json, math, re, urllib.request
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from fontTools.ttLib import TTFont as Font
from fontTools.varLib.instancer import instantiateVariableFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
C = dict(paper='#f8f7f4', ink='#1a1a2e', navy='#1f3864', deep='#141d35', blue='#2e5496', pale='#d8e4f0', muted='#596a87', line='#d8dfe8', red='#e23744', teal='#267d78', white='#ffffff')
FONTS = {
 'heading': ('ShipporiMinchoB1-Bold.ttf', 'https://raw.githubusercontent.com/google/fonts/main/ofl/shipporiminchob1/ShipporiMinchoB1-Bold.ttf'),
 'body': ('ZenKakuGothicNew-Medium.ttf', 'https://raw.githubusercontent.com/googlefonts/zen-kakugothic/main/fonts/ttf/ZenKakuGothicNew-Medium.ttf'),
 'bold': ('ZenKakuGothicNew-Bold.ttf', 'https://raw.githubusercontent.com/googlefonts/zen-kakugothic/main/fonts/ttf/ZenKakuGothicNew-Bold.ttf'),
 'en': ('HankenGrotesk.ttf', 'https://raw.githubusercontent.com/google/fonts/main/ofl/hankengrotesk/HankenGrotesk%5Bwght%5D.ttf'),
}

def fonts(cache):
    cache.mkdir(parents=True, exist_ok=True)
    manifest = {}
    locked = json.loads((HERE / 'fonts.lock.json').read_text())
    for family, (name, url) in FONTS.items():
        file = cache / name
        if not file.exists():
            req = urllib.request.Request(url, headers={'User-Agent':'Ozaken-PDF-Builder/1.0'})
            with urllib.request.urlopen(req, timeout=60) as response:
                file.write_bytes(response.read())
        manifest[name] = dict(url=url, sha256=hashlib.sha256(file.read_bytes()).hexdigest())
        if manifest[name] != locked[name]:
            raise ValueError(f'Font differs from reviewed version: {name}')
        if family == 'en':
            static = cache / 'HankenGrotesk-650.ttf'
            if not static.exists():
                instantiateVariableFont(Font(file), {'wght':650}, inplace=True).save(static)
            file = static
        pdfmetrics.registerFont(TTFont(family, str(file)))
    return manifest

# Japanese line breaking keeps Latin words together and avoids leading punctuation.
def lines(text, width, size, font='body'):
    out=[]
    for para in str(text).split('\n'):
        line=''
        tokens=re.findall(r'[A-Za-z0-9_./:@#%+\-]+|.', para)
        for token in tokens:
            if pdfmetrics.stringWidth(token,font,size)>width:
                chunks=list(token)
            else:
                chunks=[token]
            for piece in chunks:
                if line and pdfmetrics.stringWidth(line+piece,font,size)>width and piece not in '、。，．！？）』」】':
                    out.append(line.rstrip()); line=''
                line+=piece
        out.append(line.rstrip())
    return out

class Page:
    def __init__(self, cv, data, index, total, book):
        self.cv=cv; self.d=data; self.index=index; self.book=book
        self.w=960; self.h=1357.7 if data.get('portrait') else (678.8 if book=='measures' else 540)
        size=(595.276,841.89) if data.get('portrait') else ((841.89,595.276) if book=='measures' else (960,540))
        cv.setPageSize(size); cv.saveState(); cv.scale(size[0]/self.w, size[1]/self.h)
        self.dark=data.get('dark',False) or data.get('kind')=='cover'
        self.fg='white' if self.dark else 'ink'; self.muted='pale' if self.dark else 'muted'
        self.rect(0,0,self.w,self.h,'deep' if self.dark else 'paper')
        cv.bookmarkPage(f'p{index}')
        cv.addOutlineEntry(data['title'].replace('\n',' '),f'p{index}',0)
        self.text(f'OZAKEN  /  {book.upper()}  /  2026.09',48,self.h-25,600,9,'en',self.muted)
        self.text(f'{index:02d} / {total:02d}',836,self.h-27,76,10,'en',self.muted,align='right')
        self.bottom=self.h-54
    def color(self,key): return HexColor(C.get(key,key))
    def rect(self,x,y,w,h,fill,stroke=None,r=0):
        c=self.cv;c.setFillColor(self.color(fill));c.setStrokeColor(self.color(stroke or fill));c.setLineWidth(.6)
        if r:c.roundRect(x,self.h-y-h,w,h,r,fill=1,stroke=int(bool(stroke)))
        else:c.rect(x,self.h-y-h,w,h,fill=1,stroke=int(bool(stroke)))
    def line(self,x1,y1,x2,y2,color='line',width=1):
        self.cv.setStrokeColor(self.color(color));self.cv.setLineWidth(width);self.cv.line(x1,self.h-y1,x2,self.h-y2)
    def text(self,txt,x,y,w,size=16,font='body',color=None,leading=None,align='left',max_h=None):
        unsupported={ch for ch in str(txt) if not ch.isspace() and ord(ch) not in pdfmetrics.getFont(font).face.charWidths}
        if unsupported:raise ValueError(f'p{self.index} missing glyphs in {font}: {unsupported}')
        ls=lines(txt,w,size,font); lead=leading or size*1.48
        height=len(ls)*lead
        if max_h is not None and height>max_h+.1: raise ValueError(f"p{self.index} text overflow {height:.1f}>{max_h}: {txt[:70]}")
        for i,s in enumerate(ls):
            sw=pdfmetrics.stringWidth(s,font,size)
            xx=x+(w-sw if align=='right' else (w-sw)/2 if align=='center' else 0)
            self.cv.setFillColor(self.color(color or self.fg));self.cv.setFont(font,size)
            self.cv.drawString(xx,self.h-y-size-i*lead,s)
        return height
    def header(self):
        self.text(self.d.get('eyebrow','PRACTICAL GUIDE'),48,31,820,10,'en',self.muted)
        t=self.text(self.d['title'],48,58,864,29,'heading',leading=39)
        y=58+t+12
        if self.d.get('lead'): y+=self.text(self.d['lead'],48,y,852,15,color=self.muted,leading=23)+22
        else:y+=12
        return y
    def link(self,label,url,x,y,w=864,size=12):
        h=self.text(label,x,y,w,size,'body','pale' if self.dark else 'blue')
        self.cv.linkURL(url,(x,self.h-y-h,x+w,self.h-y),relative=1,thickness=0)
        return h
    def arrow(self,x1,y1,x2,y2,color='blue'):
        self.line(x1,y1,x2,y2,color,1.4)
        a=math.atan2(y2-y1,x2-x1);s=7
        for da in [-.5,.5]:self.line(x2,y2,x2-s*math.cos(a+da),y2-s*math.sin(a+da),color,1.4)
    def block(self,b,y):
        typ=b['type']; gap=b.get('gap',18); available=self.bottom-y
        if typ=='band':
            size=b.get('size',17); h=len(lines(b['text'],816,size,'bold'))*size*1.5+28
            self.rect(48,y,864,h,'navy' if self.dark else 'pale',r=4)
            self.text(b['text'],70,y+13,820,size,'bold','white' if self.dark else 'navy')
        elif typ=='text':
            h=self.text(b['text'],48,y,864,b.get('size',17),color=b.get('color',self.fg))
        elif typ=='cards':
            items=b['items']; n=len(items); gutter=20; w=(864-gutter*(n-1))/n
            body=b.get('size',16); head=b.get('head_size',21)
            heights=[len(lines(a['title'],w-36,head,'heading'))*head*1.4+len(lines(a['text'],w-36,body))*body*1.5+66 for a in items]
            h=max(heights)
            if b.get('height'):h=b['height']
            for i,a in enumerate(items):
                x=48+i*(w+gutter);self.rect(x,y,w,h,'navy' if self.dark else 'white',r=6)
                self.text(a.get('label',f'{i+1:02d}'),x+18,y+14,w-36,10,'en','pale' if self.dark else 'blue')
                th=self.text(a['title'],x+18,y+37,w-36,head,'heading',leading=head*1.4)
                self.text(a['text'],x+18,y+th+51,w-36,body,leading=body*1.5,max_h=h-th-60)
        elif typ=='table':
            widths=[864*x/sum(b['widths']) for x in b['widths']]; size=b.get('size',15)
            headers=b['headers']; rh=b.get('row_height'); yy=y
            for ri,row in enumerate([headers]+b['rows']):
                f='bold' if ri==0 else 'body'; heights=[len(lines(str(t),w-24,size,f))*size*1.42+22 for t,w in zip(row,widths)]
                hh=max(heights) if rh is None or ri==0 else max(max(heights),rh)
                xx=48
                for ci,(t,w) in enumerate(zip(row,widths)):
                    bg=('navy' if not self.dark else 'blue') if ri==0 else ('#203253' if self.dark else ('white' if ri%2 else '#eef1f6'))
                    self.rect(xx,yy,w,hh,bg)
                    self.text(str(t),xx+12,yy+10,w-24,size,f,'white' if ri==0 else self.fg,leading=size*1.42)
                    xx+=w
                yy+=hh
            h=yy-y
        elif typ=='steps':
            items=b['items']; size=b.get('size',16); yy=y
            for i,a in enumerate(items):
                self.text(a.get('label',f'{i+1:02d}'),50,yy+1,48,23,'en','pale' if self.dark else 'blue')
                hh=self.text(a['title'],110,yy,798,20,'bold',leading=28)
                hh+=self.text(a['text'],110,yy+hh+5,790,size,color=self.muted,leading=size*1.5)+5
                yy+=hh+19
                if i<len(items)-1:self.line(110,yy-9,912,yy-9,'blue' if self.dark else 'line')
            h=yy-y-12
        elif typ=='prompt':
            size=b.get('size',15); text=b['text']; ls=lines(text,816,size)
            h=len(ls)*size*1.48+38
            self.rect(48,y,864,h,'navy' if self.dark else 'white','blue' if self.dark else 'line',r=5)
            self.rect(48,y,4,h,'teal')
            self.text(text,70,y+18,816,size,leading=size*1.48)
        elif typ=='flow':
            items=b['items']; n=len(items); w=(864-28*(n-1))/n; h=b.get('height',188)
            for i,a in enumerate(items):
                x=48+i*(w+28);self.rect(x,y,w,h,'navy' if self.dark else 'white',r=6)
                self.text(a.get('label',f'{i+1:02d}'),x+16,y+16,w-32,11,'en','pale' if self.dark else 'teal')
                th=self.text(a['title'],x+16,y+43,w-32,23,'heading',leading=32)
                self.text(a['text'],x+16,y+th+55,w-32,15,max_h=h-th-62)
                if i<n-1:self.arrow(x+w+4,y+h/2,x+w+24,y+h/2,'pale' if self.dark else 'blue')
        elif typ=='links':
            yy=y
            for a in b['items']:
                yy+=self.link(a['title'],a['url'],48,yy,size=b.get('size',12))+3
                if a.get('show_url',True):yy+=self.link(a['url'],a['url'],48,yy,size=10)+12
            h=yy-y
        elif typ=='worksheet':
            yy=y
            for item in b['items']:
                self.text(item['title'],48,yy,864,21,'bold'); yy+=39
                if item.get('hint'):yy+=self.text(item['hint'],48,yy,864,17,color=self.muted)+12
                self.rect(48,yy,864,item.get('height',100),'white','line',r=4)
                for dy in range(42,item.get('height',100),42):self.line(65,yy+dy,895,yy+dy,'line',.5)
                yy+=item.get('height',100)+27
            h=yy-y
        else:raise ValueError(typ)
        if y+h>self.bottom+.2:raise ValueError(f"{self.book} p{self.index} {typ} below footer {y+h:.1f}>{self.bottom}")
        return y+h+gap
    def cover(self):
        # Abstract orbit and light traces; no content is encoded in decoration.
        c=self.cv
        for radius in [130,200,270,340]:
            c.setStrokeColor(self.color('#293c5b'));c.setLineWidth(.8)
            c.circle(875,self.h-215,radius,fill=0,stroke=1)
        for x,y in [(716,92),(844,328),(934,192)]:
            c.setFillColor(self.color('teal'));c.circle(x,self.h-y,4,fill=1,stroke=0)
        self.rect(48,92,43,4,'red')
        self.text(self.d.get('eyebrow','PRACTICAL GUIDE'),48,53,650,12,'en','pale')
        hh=self.text(self.d['title'],48,132,775,45,'heading',leading=62)
        self.text(self.d['lead'],50,hh+155,700,18,color='pale',leading=30)
        self.text('小澤健祐（おざけん）',50,self.h-110,600,18,'bold')
        self.text('一般社団法人AICX協会 代表理事',50,self.h-78,600,12,color='pale')
    def poster(self,groups):
        self.text('AI TRANSFORMATION  /  MASTER LIST',38,28,700,10,'en','pale')
        self.text('AI推進の51施策マスター',38,52,780,29,'heading')
        self.text('全体を見渡す1枚 ＋ 次ページから始め方のガイド',40,100,800,12,color='pale')
        self.text('51',827,38,92,46,'en',align='right')
        self.text('9 CATEGORIES',808,97,112,10,'en',align='right')
        idx=1; top=142; gap=15; w=(884-2*gap)/3; row_h=[139,139,173]
        for gi,g in enumerate(groups):
            row,col=divmod(gi,3); y=top+sum(row_h[:row])+gap*row; x=38+col*(w+gap); h=row_h[row]
            self.rect(x,y,w,h,'#203253',r=5)
            self.text(g['title'],x+12,y+11,w-65,16,'heading')
            detail_page=[4,5,6,7,8,9,10,12,13][gi]
            self.text(f'p.{detail_page}',x+w-45,y+14,32,10,'en','pale',align='right')
            self.line(x+12,y+39,x+w-12,y+39,'#536786',.7)
            for k,name in enumerate(g['items']):
                self.text(f'{idx:02d}',x+12,y+49+k*15,24,9,'en','pale')
                self.text(name,x+39,y+48+k*15,w-50,10,'body','white',leading=14,max_h=15)
                idx+=1
        assert idx==52
        self.text('番号は優先順位ではありません  困りごとから最初の施策を選ぶ → p.2',38,642,870,11,color='pale')
    def finish(self):
        if self.d.get('qr'):
            from reportlab.graphics.barcode.qr import QrCodeWidget
            from reportlab.graphics.shapes import Drawing
            from reportlab.graphics import renderPDF
            q=self.d['qr']; x=q['x']; y=q['y']; size=108
            code=QrCodeWidget(q['url'],barLevel='M',barBorder=4)
            x0,y0,x1,y1=code.getBounds(); w=x1-x0; h=y1-y0
            drawing=Drawing(size,size,transform=[size/w,0,0,size/h,0,0]);drawing.add(code)
            self.rect(x-6,y-6,size+12,size+12,'white')
            renderPDF.draw(drawing,self.cv,x,self.h-y-size)
            self.link(q['label'],q['url'],x-10,y+size+12,size+20,11)
        self.cv.restoreState();self.cv.showPage()

def build(book, root):
    data=json.loads((HERE/(book+'.json')).read_text())
    path=root/data['path']; path.parent.mkdir(parents=True,exist_ok=True)
    cv=canvas.Canvas(str(path), pageCompression=1, invariant=1)
    cv.setTitle(data['title']);cv.setAuthor('小澤健祐（おざけん） / 一般社団法人AICX協会');cv.setSubject('初心者向け実践ガイド / 2026年9月14日改訂')
    for i,d in enumerate(data['pages'],1):
        p=Page(cv,d,i,len(data['pages']),book)
        if d.get('kind')=='cover':p.cover()
        elif d.get('kind')=='poster':p.poster(data['groups'])
        else:
            y=p.header()
            for block in d.get('blocks',[]):y=p.block(block,y)
        p.finish()
    cv.save()
    from pypdf import PdfReader
    reader=PdfReader(path)
    assert len(reader.pages)==len(data['pages'])
    return dict(path=data['path'],pages=len(reader.pages),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())

def main():
    a=argparse.ArgumentParser();a.add_argument('--output-root',type=Path,default=ROOT);a.add_argument('--font-cache',type=Path,default=Path.home()/'.cache/ozaken-pdf-fonts');a.add_argument('--only',choices=['levels','business','measures']);a.add_argument('--manifest',type=Path)
    args=a.parse_args(); manifest=dict(fonts=fonts(args.font_cache),outputs=[])
    for book in ([args.only] if args.only else ['levels','business','measures']):manifest['outputs'].append(build(book,args.output_root))
    if args.manifest:args.manifest.parent.mkdir(parents=True,exist_ok=True);args.manifest.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(manifest['outputs'],ensure_ascii=False,indent=2))
if __name__=='__main__':main()
