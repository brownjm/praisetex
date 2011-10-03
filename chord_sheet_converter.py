#!/usr/bin/python
#    praiseTex - simple set of programs for creating praise music material, 
#    such as guitar chord sheets and presentation slides
#
#    Copyright (C) 2011 Jeffrey M Brown
#    brown.jeffreym@gmail.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Converts chord placement in typical guitar chords sheets found online 
into proper song files.

Example:

G         D   G            Bm           C           D7  G
Praise ye the Lord, the Al-might-y, the King of cre-a - tion!

G    D     G               Bm        C              D7 G 
O my soul, praise Him, for He is thy health and sal-va-tion!


Will be converted into the following:

\chord{G}Praise ye \chord{D}the \chord{G}Lord, the Al-\chord{Bm}might-y, the \chord{C}King of cre-\chord{D7}a - \chord{G}tion!

\chord{G}O my \chord{D}soul, \chord{G}praise Him, for \chord{Bm}He is thy \chord{C}health and sal-\chord{D7}va-\chord{G}tion!
"""

import re
import sys

class ChordsWordsPair(object):
    """Represents a line of words and their associated chords"""
    def __init__(self, chordline, wordline):
        self.chordline = chordline
        self.wordline = wordline.ljust(len(chordline))

    def combine(self):
        """Places chords within wordline"""
        regex = re.compile("[A-G]")
        matches = regex.finditer(self.chordline)
        # chords and their associated positions
        chords = list(zip([match.start() for match in matches], self.chordline.split()))
        chords.reverse()
        for chord in chords:
            self.wordline = self.insert(self.wordline, chord)
        return self.wordline[:-1] + r"\\" + self.wordline[-1]

    def insert(self, string, chord):
        loc, ch = chord
        return string[:loc] + "\chord{{{}}}".format(ch) + string[loc:]
        

class ChordConverter(object):
    """Converts typical guitar chord sheet into song file format"""
    def __init__(self):
        self.songfilelines = []

    def convert(self, filename):
        linecount = 0 # num of lines modified
        with open(filename) as f:
            # look for pairs of chord line followed by word line
            line = f.readline()
            while len(line) > 0:
                if self.isChords(line):
                    nextline = f.readline()
                    linecount += 1
                    self.songfilelines.append(ChordsWordsPair(line, nextline).combine())
                else:
                    self.songfilelines.append(line)
                line = f.readline()

        newname = filename + ".tex"
        with open(newname, "w") as f:
            f.write("\subsection{}\n\\by{}\n\comment{}\n")
            f.writelines(self.songfilelines)
        msg = "Wrote file: {}\nWas able to insert chords into {} lines"
        print msg.format(newname, linecount)

    def isChords(self, line):
        if not containsAny(line, notChords) and len(line.strip()) > 0:
            return True
        else:
            False


def containsAny(line, letters):
    for letter in letters:
        if letter in line:
            return True
    return False

def containsOnly(line, letters):
    for c in line:
        if c.isalnum():
            if c in letters:
                continue
            else:
                return False
        else:
            continue

    return True
        

notChords = "HJKLOPQRTVWXYZ"
chords = "ABCDEFGminajsugd123456789"

if __name__ == "__main__":
    if len(sys.argv) is 1:
        raise IOError("Please supply a filename as argument")
    c = ChordConverter()
    c.convert(sys.argv[1])
