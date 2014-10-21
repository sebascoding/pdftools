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
from xref import Xref
from trailer import Trailer
from info import Info

class Metadata(object):
    """ Implements the abstraction and asociated methods for pdf metadata
    representation"""
    def __init__(self, pdf):
        self.pdf = pdf
        self.title = ''
        self.author = ''
        self.subject = ''
        self.keywords = ''
        self.creator = ''
        self.producer = ''
        self.creationdate = ''
        self.moddate = ''
        self.key_num = -1

    def loads(self):

        pdf = pdflib.PDFFile(self.pdf, 'r')

        startxref = -1
        islinearized = pdf.is_linearized()

        if islinearized:
            startxref = Xref.first_xref_offset(pdf)

        trailer = Trailer(pdf)
        trailer.parse(offset=startxref)

        info_ref = trailer.info

        xref = Xref(pdf)

        if islinearized:
            xref.parse_xref(offset=startxref,)
            xref.parse_xref(offset=trailer.prev_offset)
        else:
            xref.parse_full_xref()

        info_offset = xref.get_object(info_ref.num, info_ref.gen_number).offset

        info = Info(pdf)
        info.parse(offset=info_offset)

        self._info2meta(info)

    def dumps(self):
        pass

    def get_metadata(self):
        """ Returns a dictionary with non None metadata key-value pairs"""
        return self.__dict__

    def _info2meta(self, info):
        for key in info.__dict__.viewkeys():
            if key in self.__dict__.viewkeys():
                self.__dict__[key] = info.__dict__[key]

        self.key_num = 0

    def __str__(self):

        metastr = ''

        for key in self.__dict__:
            if key != 'pdf':
                metastr += "%s: %s\n" % (key.title(), self.__dict__[key])
            
        return metastr

meta = Metadata('./prev1.pdf')
meta.loads()
print meta
