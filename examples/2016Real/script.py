import fitz
import glob

files = glob.glob('/eos/user/g/gpizzati/www/rdf/2016_full6_topcr/*.pdf')
for file in files:
    print('Converting file', file)
    doc = fitz.open(file)
    page = doc.load_page(0)
    pixmap = page.get_pixmap(dpi=200)
    pixmap.save(file[:-len('.pdf')] + '_high_res.png')
    img = pixmap.tobytes()
 
#fname = '/eos/user/g/gpizzati/www/rdf/2016_full6_topcr/topcr_mm_ptl1'
#doc = fitz.open(fname + '.pdf')
#page = doc.load_page(0)
#pixmap = page.get_pixmap(dpi=200)
#pixmap.save(fname + '1.png')
#img = pixmap.tobytes()
