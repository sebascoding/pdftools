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

import types
import sys
import re
import chardet
import io
import pdb

#====== Character's classes ======
ANY = -1
WHITESPACE = 0
DELIMITER = 1
REGULAR = 2
#=================================

excluded_chars = [u'\x00', u'\xfe', u'\xff']

def is_whitespace(ch):
    return ord(ch) in (0, 9, 10, 12, 13, 32)

def is_delimiter(ch):
    return ord(ch) in (37, 40, 41, 47, 60, 62, 91, 93, 123, 125)

def is_regular(ch):
    return (not is_whitespace(ch)) and (not is_delimiter(ch))

def get_char_class(ch):
    if is_whitespace(ch):
        return WHITESPACE
    elif is_delimiter(ch):
        return DELIMITER
    else:
        return REGULAR

def parse_pdfstr(pdfstr):

    (idx, j, k) = (0, 0, 0)
    balance = 0
    size = len(pdfstr)

    token = ''

    # Find opening character
    if '(' in pdfstr:
        idx = pdfstr.index('(')
    elif '<' in pdfstr:
        idx = pdfstr.index('<')

    # If the first character is a left bracket we have a Literal String
    if pdfstr[idx] == '(':

        idx += 1
        balance += 1

        while idx < size:

            # Literal strings may have balanced brackets inside.
            if pdfstr[idx] == '(':
                balance += 1
            elif pdfstr[idx] == ')':
                balance -= 1
                if balance == 0:
                    break

            if ord(pdfstr[idx]) in range (32, 128):

                token += pdfstr[idx]
                j += 1
            else:
                ch = pdfstr[idx].decode(chardet.detect(pdfstr[idx])['encoding'])
                if ch not in excluded_chars:
                    try:
                        token += ch.encode('utf-8')
                        j += 1
                    except Exception, e:
                        print e


            idx += 1

        if balance != 0:
            token = ''

    elif pdfstr[idx] == '<': # It is an Hexadecimal String

        pdfstr = pdfstr[1:-1]
        size = len(pdfstr)
        if size%2 != 0: pdfstr + '0'
        token = ''.join(chr(int(pdfstr[i:i+2], 16)) for i in range(0, size, 2))

    return token

def unescape_pdfstr(pdfstr):

    size = len(pdfstr)
    
    if size == 0:
        return ''

    idx = 0

    newstr = pdfstr.split('\\')

    for idx, s in enumerate(newstr):
        if len(s) > 0:
            if len(s) >= 3:
                try:
                    # Converting octal to char
                    newstr[idx] = chr(int(s[0:3], 8)) + s[3:]
                except:
                    pass

                continue

            if s[0] not in ('(', ')'):
                newstr[idx] = s[1:]
        else:
            newstr[idx] = '\\'

    return ''.join(newstr)


class PDFFile(file):

    def __init__(self, *args, **kwargs):
        file.__init__(self, *args, **kwargs)

    def get_prev_line(self, offset=-1):


#        pdb.set_trace()
        if offset != -1:
            self.seek(offset)

        ch = self.read(1)
        line = ''

        while ch in (chr(0x0D), chr(0x0A)):
            self.seek(-2, 1)
            ch = self.read(1)

        self.seek(-1, 1)

        while ch not in (chr(0x0D), chr(0x0A)):
            off = self.tell()

            if off > 1:
                self.seek(-2, 1)
            else:
                self.seek(0)
                line = self.readline().strip()
                break
            ch = self.read(1)

        i = 1
        size = len(line)
        if line == '':
            #pdb.set_trace()
            line = self.readline()
            line = line.split(chr(0X0D))
            if len(line) > 1:
                i += 1
            size = sum(map(len, line)) + len(line) - 1
            line = line[0]
        #pdb.set_trace()

        #print "prev: %s" % self.tell()
        #print "len: %s" % len(line)
        self.seek(-(size + 1), 1)
        #print "after: %s" % self.tell()

        #print line.strip()

        if self.tell() <= 2:
            raise Exception("Reached first line")

        return line.strip()


    def get_pdf_size(self, pdf):

        off = self.tell()
        self.seek(0, 2)
        size = self.tell()
        self.seek(off)

        return size

    def next_token(self, char_class=ANY, delimiter=' '):

        ''' Get token by character class or by specific string delimiter '''
        def condition(ch):
            
            if ch != '':
                if char_class != ANY:
                    check = {WHITESPACE:is_whitespace, DELIMITER:is_delimiter, REGULAR:is_regular}
                    return check[char_class](ch)
                else:
                    return ch == delimiter

        size = len(delimiter) if char_class == ANY else 1
        #print size

        first_off = self.tell()

        ch = self.read(size)
        
        #print "CHAR: %s\n" % ch
        #print self.tell()

        while condition(ch): ch = self.read(size)
        while not condition(ch):
            ch = self.read(size)
            #print ch
            self.seek(1 - size, 1)

        last_off = self.tell()

        self.seek(first_off)
        line = self.read(last_off - first_off - 1)
        self.seek(size, 1)

        return line

    def parse_object(self, offset=-1):

        #pdb.set_trace()

        if offset != -1:
            self.seek(offset)

        ch = self.read(3)

        while ch != '':
            if ch == 'obj':
                self.seek(2, 1)
                break
            else:
                ch = self.read(3)
                self.seek(-2, 1)

        return self.next_token(delimiter='endobj').split('<<')[-1].split('>>')[0]

    def is_linearized(self):
        return 'Linearized' in self.parse_object(0)

class PDFDate(object):

    def __init__(self):
        self.year = ''
        self.month = ''
        self.day = ''
        self.hour = ''
        self.minute = ''
        self.second = ''
        self.offsetsign = ''
        self.houroffset = ''
        self.minuteoffset = ''

    def parse(self, datestr):

        #pdb.set_trace()

        idx = re.search('\d', datestr)

        if not idx:
            return
        else:
            idx = idx.start()
            datestr = datestr[idx:]

        self.year = datestr[0:4]

        auxstr = (datestr[i:i+2] for i in range(4, 14, 2))
        (self.month, self.day, self.hour, self.minute, self.second) = auxstr

        size = len(datestr)

        if size > 14:

            self.offsetsign = datestr[14]
            self.houroffset = datestr[15:17]

            if size > 17 and datestr[17] == '\'':
                self.minuteoffset = datestr[18:20]

    def __str__(self):

        datestr = "%s/" % self.year
        datestr += "%s/" % self.month
        datestr += "%s " % self.day
        datestr += "%s:" % self.hour
        datestr += "%s:" % self.minute
        datestr += "%s" % self.second

        return datestr
