#!/usr/bin/env python
 
from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
 
styles = getSampleStyleSheet()
HeaderStyle = styles["Heading1"]
H4Style = styles["Heading4"]
ParaStyle = styles["Normal"]
PreStyle = styles["Code"] 

def header(txt, style=HeaderStyle, klass=Paragraph, sep=0.3):
    s = Spacer(0.2*inch, sep*inch)
    para = klass(txt, style)
    sect = [s, para]
    result = KeepTogether(sect)
    return result
 
def p(txt):
    return header(txt, style=ParaStyle, sep=0.1)
 
def pre(txt):
    s = Spacer(0.1*inch, 0.1*inch)
    p = Preformatted(txt, PreStyle)
    precomps = [s,p]
    result = KeepTogether(precomps)
    return result
 
def table(tableDict):
    data = []
    for spec, value in tableDict.iteritems():
        data.append([spec, value])
    
    t = Table(data)
    ts = TableStyle([('FONT', (0, 0), (-1, -1), 'Helvetica', 8)])
    t.setStyle(ts)
    return t

def image(imageFilename, style=H4Style, width=None):
    im = Image(imageFilename)
    #imdraw = svg2rlg(imageFilename)
    if width is not None:
        ratio = im.drawHeight / float(im.drawWidth)
        im.drawWidth = width
        im.drawHeight = width * ratio
    im.hAlign = 'CENTER'
    result = [im]
    #result = [KeepTogether(text, imdraw)]
    return result

def makePDF(elements, title, docName):
    doc = SimpleDocTemplate(docName, title=title)
    doc.build(elements)

