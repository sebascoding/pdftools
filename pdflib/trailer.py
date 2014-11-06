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

import pdb
import pdflib
from xref import Reference

import re

class Trailer(object):

    def __init__(self, pdf):
        self.pdf = pdf
        self.size = -1
        self.prev = -1
        self.root = None
        self.encrypt = None
        self.info = None
        self.ID = -1

    def parse(self, pdf=None, linearized=False, offset=-1):

        # If not offset is given it will find where the (first) trailer is
        if offset == -1:
            offset = self.first_offset(linearized=linearized)
            if offset == -1:
                return False
        self.pdf.seek(offset)

        while True:

            if self.pdf.read(2) == '<<':

                rawtrailer = self.pdf.next_token(delimiter='>>').split('/')

                fields = ('Size', 'Prev', 'Root', 'Encrypt', 'Info', 'ID')
                lastfield = ''

                for s in rawtrailer:
                    if len(s) > 0:
                        s = s.split()

                        if len(s) > 0:
                            if s[0] in fields:
                                lastfield = s[0]
                                if s[0] != 'ID': s[0] = s[0].lower() 
                                self.__dict__[s[0]] = s[1:]

                for k in ('size', 'prev'):
                    if self.__dict__[k] != -1:
                        self.__dict__[k] = int(self.__dict__[k][0])
                for k in ('root', 'info'):
                    if self.__dict__[k]:
                        ref = Reference(num=int(self.__dict__[k][0]),
                                        gen_number=int(self.__dict__[k][1]),
                                        key=self.__dict__[k][2])
                        self.__dict__[k] = ref

                break

            else:
                self.pdf.seek(-1,1)

    def __str__(self):
        trailerstr = "Size: %s\n" % self.size
        trailerstr +=  "Prev: %s\n" % self.prev
        trailerstr += "Root: %s\n"  % self.root
        trailerstr += "Info: %s\n"  % self.info
        trailerstr += "ID: %s\n"  % self.ID
        
        return trailerstr

    def get_prev_offset(self, offset=-1):

        if offset != -1:
            self.pdf.seek(offset)

        rawtrailer = self.pdf.next_token(delimiter='>>')
        idx = rawtrailer.find('Prev')

        if idx != -1:
            return int(re.compile("[^\d]").split(rawtrailer[idx+4:].strip())[0])
        else:
            return -1

    def first_offset(self, linearized=False):

        offset = -1

        self.pdf.seek(0, 2)
        total_size = self.pdf.tell()

        self.pdf.seek(0, 0)

        lines = self.pdf.readlines()
        cur_size = 0

        lines = reversed(lines) if not linearized else lines

        for line in lines:
            cur_size += len(line)

            if 'trailer' in line:
                if not linearized:
                    offset = total_size - cur_size
                else:
                    offset = cur_size - (len(line) - len("trailer"))
                break

        return offset

