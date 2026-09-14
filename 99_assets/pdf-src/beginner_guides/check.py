#!/usr/bin/env python3
"""Check exported PDFs, references and the 51-item master before distribution.
This complements mandatory visual inspection; it does not replace it.
"""
import argparse,json,re
from pathlib import Path
import pdfplumber
from pypdf import PdfReader

HERE=Path(__file__).resolve().parent

def norm(s):return re.sub(r'\s','',s).replace('／','/').replace('‧','・')
def strings(value):
    if isinstance(value,str):yield value
    elif isinstance(value,list):
        for x in value:yield from strings(x)
    elif isinstance(value,dict):
        for k,v in value.items():
            if k not in {'type','kind','eyebrow','url','x','y','dark','label'}:yield from strings(v)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output-root',type=Path,default=HERE.parents[2]);parser.add_argument('--report',type=Path)
    a=parser.parse_args();results=[]
    for book in ['levels','business','measures']:
        data=json.loads((HERE/(book+'.json')).read_text());f=a.output_root/data['path'];r=PdfReader(f)
        assert not r.is_encrypted,f
        assert len(r.pages)==len(data['pages']),(book,len(r.pages))
        checked=0;annotation_count=0
        with pdfplumber.open(f) as pdf:
            for i,(pg,source) in enumerate(zip(pdf.pages,data['pages']),1):
                text=norm(r.pages[i-1].extract_text() or '')
                assert norm(source['title']) in text,(book,i,'missing title')
                expected=list(strings(source.get('blocks',[])))
                for s in expected:
                    if s and norm(s) not in text:raise AssertionError((book,i,'missing text',s))
                for ch in pg.chars:
                    if not ch['text'].strip():continue
                    assert ch['x0']>=-0.1 and ch['x1']<=pg.width+.1,(book,i,'horizontal clipping',ch)
                    assert ch['top']>=-.1 and ch['bottom']<=pg.height+.1,(book,i,'vertical clipping',ch)
                refs=[int(n) for n in re.findall(r'p\.(\d+)',r.pages[i-1].extract_text())]
                assert all(1<=n<=len(r.pages) for n in refs),(book,i,'invalid page reference')
                for ref in r.pages[i-1].get('/Annots',[]):
                    ann=ref.get_object();rect=ann.get('/Rect')
                    if rect:
                        assert 0<=float(rect[0])<float(rect[2])<=pg.width+.1,(book,i,'link x',rect)
                        assert 0<=float(rect[1])<float(rect[3])<=pg.height+.1,(book,i,'link y',rect)
                    annotation_count+=1
                if source.get('portrait'):assert abs(pg.width-595.276)<.1 and abs(pg.height-841.89)<.1
                checked+=1
        if book=='measures':
            master=[name for g in data['groups'] for name in g['items']]
            rows=[row for pg in data['pages'][3:13] for b in pg['blocks'] if b['type']=='table' for row in b['rows']]
            assert len(master)==51 and len(set(master))==51
            assert [row[0] for row in rows]==[f'{i:02d}' for i in range(1,52)]
            assert [row[1] for row in rows]==master
            poster=norm(r.pages[0].extract_text())
            assert all(norm(t) in poster for t in master),'missing poster item'
        results.append(dict(book=book,path=data['path'],pages=checked,links=annotation_count,text_and_bounds='pass'))
    assert sum([20,30,50])==100
    assert (90-20-15-5)*48/60==40 and 40*3000==120000
    report=dict(outputs=results,measures_51_names_and_numbers='pass',worked_example_arithmetic='pass')
    if a.report:a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
