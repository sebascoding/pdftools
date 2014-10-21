import sys, getopt

from pdflib import pdflib
from pdflib.trailer import Trailer
from pdflib.xref import Xref
from pdflib.info import Info


def main(argv):

    try:
        opts, args = getopt.getopt(argv,"hm:",["help=","meta="])
    except getopt.GetoptError:
        print 'usage: pdftools.py -m <file.pdf>'
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print 'usage: pdftools.py -m <file.pdf>'
            sys.exit()
        elif opt in ("-m", "--meta"):
            getMeta(arg)
        else:   
            print 'usage: pdftools.py -m <file.pdf>'

def getMeta(pdfFile):

    info = None
    pdf = None

#try:
    pdf = pdflib.PDFFile(pdfFile, 'rU')

    trailer = Trailer(pdf)
    if trailer.parse() is False:
        print "Error parseando trailer"
        exit()
#print trailer

    info_ref = trailer.info
#print info_ref

    xref = Xref(pdf)
    xref.parse_full_xref()
#print xref

    info_off = xref.get_ref_offset(num=info_ref.num, gen_number=info_ref.gen_number)
#print "info: %s" % info_off

    info = Info(pdf)
    info.parse(offset=info_off)
    print info

def printLicense():

    license = '''PDFTools  Copyright (C) 2014  Sebastian Alvarez Mendez
This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
This is free software, and you are welcome to redistribute it
under certain conditions; type `show c' for details.'''

    print "\n" + license + "\n"
#except Exception, e:
#    print str(e)
#    exit()
#finally:
    #with open ("result.log", 'a') as fh:
    #    fh.write("-------------------------------\n%s\n\n" % info)

if __name__ == "__main__":
   printLicense()
   main(sys.argv[1:])

