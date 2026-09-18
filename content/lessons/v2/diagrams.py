"""Compact SVGs; positions come from equations and angle values."""
import math
from fractions import Fraction
from html import escape
from .layout import F, P, figure

BLUE='#2e65d0'
PURPLE='#8257c6'
GRAY='#7f8da4'


def svg_text(x,y,text,size=15,color='#425571',anchor='middle'):
    return f'<text x="{x:.3f}" y="{y:.3f}" text-anchor="{anchor}" font-family="Arial,sans-serif" font-size="{size}" fill="{color}">{escape(str(text))}</text>'


def svg_fraction(x,y,n,d,color='#425571',size=15):
    width=max(len(str(n)),len(str(d)))*size*.6+8
    return svg_text(x,y-6,n,size,color)+f'<line x1="{x-width/2:.2f}" y1="{y:.2f}" x2="{x+width/2:.2f}" y2="{y:.2f}" stroke="{color}"/>'+svg_text(x,y+size,d,size,color)


def pi_label(k, denominator=12):
    f=Fraction(k,denominator)
    if not f: return '0'
    n='π' if f.numerator==1 else '−π' if f.numerator==-1 else str(f.numerator).replace('-','−')+'π'
    return n if f.denominator==1 else F(n,str(f.denominator))


def circle_model(divisions, title):
    cx=cy=210; radius=139;label_r=178
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 420" width="380" role="img" aria-label="{escape(title)}">',
         '<path d="M52 210 H373 M210 368 V52" stroke="#aab6c8" stroke-width="1.2" fill="none"/><path d="M373 210 l-6 -3 v6z M210 52 l-3 6 h6z" fill="#aab6c8"/>',
         f'<circle cx="210" cy="210" r="139" stroke="{BLUE}" stroke-width="1.8" fill="none"/>']
    for i in range(divisions):
        a=2*math.pi*i/divisions
        x,y=cx+radius*math.cos(a),cy-radius*math.sin(a)
        out.append(f'<line x1="210" y1="210" x2="{x:.3f}" y2="{y:.3f}" stroke="#e1e8f4"/>')
        out.append(f'<circle data-angle-step="{i*24//divisions}" cx="{x:.3f}" cy="{y:.3f}" r="3.5" fill="{BLUE}"/>')
        lx,ly=cx+label_r*math.cos(a),cy-label_r*math.sin(a)
        f=Fraction(2*i,divisions)
        num='π' if f.numerator==1 else str(f.numerator)+'π'
        if i==0: out.append(svg_text(lx,ly-8,'0',16))
        elif f.denominator==1:out.append(svg_text(lx,ly+5,num,16))
        else:out.append(svg_fraction(lx,ly-3,num,f.denominator,size=16))
    out += [svg_text(380,233,'x',15),svg_text(229,57,'y',15),svg_text(198,226,'O',13),'</svg>']
    return ''.join(out)


def triangle_svg(kind):
    # One quarter of a unit circle, with a 45° or 30° radius.
    angle=math.pi/(4 if kind=='45' else 6)
    x=70+230*math.cos(angle); y=288-230*math.sin(angle)
    out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 390 340" width="360" role="img" aria-label="Прямоугольный треугольник в первой четверти единичной окружности">',
         '<path d="M45 288 H353 M70 307 V28" stroke="#9daec6" stroke-width="1.4" fill="none"/>',
         '<path d="M300 288 A230 230 0 0 0 70 58" stroke="#d0dff5" stroke-width="1.6" fill="none"/>',
         f'<path d="M70 288 L{x:.3f} {y:.3f} V288 Z" fill="#edf4ff" stroke="{BLUE}" stroke-width="1.8"/>',
         f'<path d="M{x-12:.3f} 288 V276 H{x:.3f}" fill="none" stroke="#a7b7cf"/>',
         f'<circle cx="{x:.3f}" cy="{y:.3f}" r="4" fill="{BLUE}"/>',
         svg_text(55,310,'O',14),svg_text(x+14,y-10,'M',16,BLUE),svg_text((70+x)/2-9,(288+y)/2-9,'1',19,BLUE),
         svg_text(350,311,'x',16),svg_text(50,32,'y',16),svg_text(55,63,'1',14),svg_text(300,310,'1',14),
         f'<path d="M112 288 A42 42 0 0 0 {70+42*math.cos(angle):.3f} {288-42*math.sin(angle):.3f}" fill="none" stroke="#7397d2" stroke-width="1.2"/>']
    if kind=='45':
        out.extend([svg_fraction((70+x)/2,310,'√2','2'),svg_fraction(x+33,(288+y)/2,'√2','2'),svg_fraction(126,264,'π','4',BLUE)])
    else:
        out.extend([svg_fraction((70+x)/2,310,'√3','2'),svg_fraction(x+31,(288+y)/2,'1','2'),svg_fraction(144,270,'π','6',BLUE)])
    return ''.join(out)+'</svg>'


def mini_power(n,d=1, color=BLUE):
    # A fixed square plot preserves equal scales in every comparison card.
    origin=175;scale=45
    out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 350 330" width="330" role="img" aria-label="График степенной функции">']
    for k in [-3,-2,-1,0,1,2,3]:
        pos=origin+scale*k
        out.append(f'<path d="M40 {pos} H310 M{pos} 40 V310" stroke="#edf1f7" fill="none"/>')
        if k and abs(k)<3:
            out.extend([svg_text(pos,origin+17,k,12),svg_text(origin-10,origin-scale*k+4,k,12,anchor='end')])
    out.append(f'<path d="M30 {origin} H319 M{origin} 315 V24" stroke="#8a9bb3" stroke-width="1.2" fill="none"/>')
    out.extend([svg_text(327,origin+4,'x',14),svg_text(origin-10,22,'y',14)])
    if d==1:
        out.append(svg_text(280,26,'y = x'+str(n).translate(str.maketrans('-0123456789','⁻⁰¹²³⁴⁵⁶⁷⁸⁹')),14,color))
    for sign in ([-1,1] if d==1 else [1]):
        path=[]
        for i in range(501):
            x=sign*3*(i/500)**(3 if 0<n/d<1 else 1)
            if x==0 and n<=0:continue
            y=x**(n/d)
            if abs(y)>3:continue
            path.append(f'{"M" if not path else "L"}{origin+scale*x:.3f},{origin-scale*y:.3f}')
        out.append(f'<path data-power="{n},{d}" d="{" ".join(path)}" fill="none" stroke="{color}" stroke-width="2.4"/>')
    return ''.join(out)+'</svg>'
