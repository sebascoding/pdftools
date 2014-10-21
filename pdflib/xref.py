#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Sebastian Alvarez Mendez
#
# This file is part of PDFTools.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import pdflib
import pdb

class Reference(object):

    def __init__(self, num=-1, offset=-1, gen_number=-1, key=''):
        self.num = num
        self.offset = offset
        self.gen_number = gen_number
        self.key = key
        
    def __str__(self):
        refstr = "Number: %s\n" % str(self.num)
        refstr += "Offset: %s\n" % str(self.offset)
        refstr += "Generation number: %s\n" % str(self.gen_number)
        refstr += "Key: %s\n" % self.key
        return refstr

import trailer

class Xref(object):

    def __init__(self, pdf):
        self.pdf = pdf
        self.num_entries = 0
        self.references = dict()

    def parse_xref(self, offset):

        self.pdf.seek(offset)

        token = self.pdf.next_token(char_class=pdflib.WHITESPACE)

        if token != 'xref':
            pass

        obj_num = int(self.pdf.next_token(char_class=pdflib.WHITESPACE))
        tot_obj = int(self.pdf.next_token(char_class=pdflib.WHITESPACE))
        left_obj = tot_obj


        token = self.pdf.next_token(char_class=pdflib.WHITESPACE)

        ref = Reference()

        while not 'trailer' in token:
            #print token
            size = len(token)
            #pdb.set_trace()
            if left_obj == 0:
                token = self.pdf.next_token(char_class=pdflib.WHITESPACE)
                left_obj = int(self.pdf.next_token(char_class=pdflib.WHITESPACE))
                tot_obj += left_obj

            elif size == 10:
                ref = Reference(num=obj_num, offset=int(token))

            elif size == 5:
                ref.gen_number = int(token)

            elif size == 1:
                if token[0] in ('n', 'f'):
                    ref.key = token[0]
                    self.add_ref(ref)
                    obj_num += 1
                    left_obj -= 1

            token = self.pdf.next_token(char_class=pdflib.WHITESPACE).strip()

        self.num_entries += tot_obj

    def parse_full_xref(self):

        #pdb.set_trace()

        self.parse_xref(self.first_xref_offset())

        tr = trailer.Trailer(self.pdf)

        offset = tr.get_prev_offset()
        prev_offset = -1

        while offset != -1 and offset != prev_offset:
            prev_offset = offset

            self.parse_xref(offset)

    def first_xref_offset(self):

        # Position at the end of the file
        self.pdf.seek(0,2)

        line = self.pdf.get_prev_line()

        while not 'startxref' in line:
            line = self.pdf.get_prev_line()
            #print line

        #print self.pdf.tell()
        self.pdf.seek(len(line)+1, 1)

        return int(self.pdf.next_token(char_class=pdflib.WHITESPACE))
        #pdb.set_trace()
        #off = int(self.pdf.next_token(char_class=pdflib.WHITESPACE))
        #print off
        #return off

    def add_ref(self, ref):
        self.references[ref.num, ref.gen_number] = ref

    def get_object(self, num, gen_number):
        return self.references[num, gen_number]

    def get_ref_offset(self, num, gen_number):

        offset = -1

        if (num, gen_number) in self.references.viewkeys():
            offset = self.references[(num, gen_number)].offset

        return offset

    def get_total_refs(self):
        return len(self.references)

    def __str__(self):

        xrefstr =  "Total objects: %s\n\n" % self.get_total_refs()

        for ref in self.references.values():
            xrefstr += "Obj num: %s\n" % ref.num
            xrefstr += "Offset: %s\n" % ref.offset
            xrefstr += "Gen num: %s\n" % ref.gen_number
            xrefstr += "Key: %s\n\n" % ref.key
            
        return xrefstr
