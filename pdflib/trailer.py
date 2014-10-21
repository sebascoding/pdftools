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

    def parse(self, pdf=None, offset=-1):

        #pdb.set_trace()
        # If not offset is given it will find where the (first) trailer is
        if offset == -1:
            offset = self.first_offset()
            if offset == -1:
                return False    
        self.pdf.seek(offset)

        while True:

            if self.pdf.read(2) == '<<':

                rawtrailer = self.pdf.next_token(delimiter='>>').split('/')

                fields = ('Size', 'Prev', 'Root', 'Encrypt', 'Info', 'ID')
                lastfield = ''

                #print rawtrailer

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

                #for k in self.__dict__.viewkeys():
                    #try:
                        #self.__dict__[k] = int(self.__dict__[k])
                    #except:
                        #pass

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

    def first_offset(self):

        offset = -1

        self.pdf.seek(0, 2)

        size = self.pdf.tell()

        while self.pdf.tell() >= size - size/2:

            #print self.pdf.tell()

            line = self.pdf.get_prev_line()

            if line == 'trailer':
                offset = self.pdf.tell()
                break

        return offset

        #//====== Temporary fix for pure xref streams pdfs ===============
        #for (i = 0 i < 10 i++)
        #{
            #offset = get_prev_line(&line, &size, pdf, offset)

            #if (!line)
                #return -1
            
    #//  		printf("%s\n", line)
            
            #if (strncmp(line, "startxref", (size < 9 ? size : 9) ) == 0)
            #{
                #// Needed, get_prev_line gives you the offset but doesn't move
                #fseek(pdf, offset, SEEK_SET)
                
                #char c1 = '\0'
                
                #while ((c1 = fgetc(pdf)) != '>')
                #{
    #// 				if (is_whitespace(c1))
    #// 					puts("white")
    #// 				else
    #// 					printf("%c\n", c1)
                    #offset--
                    #fseek(pdf, offset, SEEK_SET)
                #}
                
    #// 			printf("%c\n", c1)
                
                #offset--
                #fseek(pdf, offset, SEEK_SET)
                
                #char c[] = {fgetc(pdf),fgetc(pdf)}
                
    #// 			printf("%c,%c\n", c[0],c[1])
                
                #if (c[0] != '>' || c[1] != '>')
                #{
                    #puts("Stream Xref")
                    #offset = -1 // With this it avoids searching for stream xref instead of trailer
                #}
                
                #free(line)
                #line = NULL
                
                #break
            #}
            
            #free(line)
            #line = NULL
        #}
        #// ===================================================

        #return -1

