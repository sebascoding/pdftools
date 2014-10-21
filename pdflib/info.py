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
import re

class Info(object):

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
        self.trapped = ''

    def parse(self, offset=-1):

        fields = ('Title', 'Author', 'Subject', 'Keywords', 'Creator',
                  'Producer', 'CreationDate', 'ModDate', 'Trapped')

        infostr = self.pdf.parse_object(offset)

        #print infostr

        lastword = None
        strindex = 0
        wordindex = 0
        lastindex = 0

        while wordindex != -1:

            wordindex = infostr[strindex:].find('/')

            if wordindex != -1:
                
                wordindex += strindex

                if wordindex + 1 >= len(infostr):
                    break

                word = re.compile("[^\w]").split(infostr[wordindex+1:])[0]

                if word in fields:
                    if lastword is not None:
                        self.__dict__[lastword.lower()] = infostr[0:wordindex].strip()
                    
                    lastword = word
                    infostr = infostr[wordindex+1+len(lastword):]
                else:
                    strindex = wordindex + 1

        if lastword is not None and lastword not in self.__dict__.keys():
            self.__dict__[lastword.lower()] = infostr.strip()    

#       lastfield = ''

#       for s in infostr:
#           if len(s) > 0:
#               idx = s.find('(')
#               if idx == -1: continue
#               if s[0:idx] in fields:
#                   self.__dict__[s[0:idx].lower()] = s[idx:]

        for k in self.__dict__.keys():
            if 'date' in k and self.__dict__[k] != '':
                date = pdflib.PDFDate()
                date.parse(self.__dict__[k])
                self.__dict__[k] = date
            elif k == 'trapped' and self.__dict__[k] != '':
                if 'True' in self.__dict__[k]:
                    self.__dict__[k] = True
                else:
                    self.__dict__[k] = False
            elif k != 'pdf' and len(self.__dict__[k]) > 0:
                s = pdflib.parse_pdfstr(self.__dict__[k])
                self.__dict__[k] = pdflib.unescape_pdfstr(s)

        #print self.__dict__

    def __str__(self):

        infostr = ''

        for key in self.__dict__:
            if key != 'pdf' and self.__dict__[key] != '':
                infostr += "%s: %s\n" % (key.title(), self.__dict__[key])

        return infostr
