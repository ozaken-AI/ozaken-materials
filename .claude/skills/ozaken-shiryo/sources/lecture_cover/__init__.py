"""Shared, deterministic cover decoration for the catalogue and every material."""
def curtain():
    return '<div class="tl-curtain" aria-hidden="true"><div class="tl-curtain-sheet">'+''.join(f'<i style="--rib:{i}"></i>' for i in range(20))+'</div><div class="tl-curtain-glow"></div><span class="tl-curtain-line"></span></div>'

def cover_air():
    """Sparse decorative light; deterministic positions keep rebuilds reproducible."""
    points = [(18,18),(32,76),(43,12),(48,58),(54,87),(60,29),(65,69),
              (70,10),(74,48),(78,83),(83,24),(87,61),(91,40),(95,77)]
    particles = ''.join(
        f'<i style="--x:{x}%;--y:{y}%;--drift:{24+i%4*14}px;--duration:{12+i%5*2}s;--delay:{-i*1.7}s;--size:{2+i%3}px"></i>'
        for i,(x,y) in enumerate(points))
    return '<div class="tl-cover-air" aria-hidden="true">'+particles+'<span class="tl-cover-ray"></span><span class="tl-cover-ray"></span></div>'
