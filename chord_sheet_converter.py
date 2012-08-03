#!/usr/bin/python
#    praiseTex - simple set of programs for creating praise music material, 
#    such as guitar chord sheets and presentation slides
#
#    Copyright (C) 2012 Jeffrey M Brown
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
        self.wordline = wordline.ljust(len(chordline)) # make same length

    def combine(self):
        """Places chords within wordline"""
        regex = re.compile("[A-G]") # valid chords
        matches = regex.finditer(self.chordline)

        # chords and their associated positions: list of (location, chord)
        chords = list(zip([match.start() for match in matches], 
                          self.chordline.split()))
        
        # Must insert chords from end to beginning of wordline,
        # since each chord insertion shifts the position of subsequent chords
        chords.reverse()
        for chord in chords:
            self.wordline = self.insert(self.wordline, chord) # insertion
        return self.wordline[:-1] + r"\\" + self.wordline[-1] # add newline: \\

    def insert(self, string, chord):
        """Wraps chord in latex command \chord{}, and inserts it into string"""
        loc, ch = chord
        ch = ch.replace('#', '\#')  # latex requires backslash before #-symbol
        return string[:loc] + "\chord{{{}}}".format(ch) + string[loc:]
        

class ChordConverter(object):
    """Converts typical guitar chord sheet into latex song file format"""
    def __init__(self):
        self.songfilelines = [] # holds text for converted song file

    def convert(self, filename):
        linecount = 0 # num of lines modified
        with open(filename) as f:
            # look for pairs of chord line followed by word line
            line = f.readline()
            while len(line) > 0:
                if self.isChords(line): # valid chordline
                    nextline = f.readline() # get wordline below it
                    linecount += 1
                    # combine chords and words together
                    self.songfilelines.append(ChordsWordsPair(line, nextline).combine())
                else: # not a valid chordline, place in song file as is
                    self.songfilelines.append(line)
                line = f.readline() # get next line

        newname = filename + ".tex" # add latex extension
        with open(newname, "w") as f:
            # add song file header and write out file
            f.write("\songtitle{}\n\\by{}\n\comment{}\n")
            f.writelines(self.songfilelines)

        # print out final status of conversion
        msg = "Wrote file: {}\nWas able to insert chords into {} lines"
        print(msg.format(newname, linecount))

    def isChords(self, line):
        """Check if line contains chords"""
        if not containsAny(line, notChords) and len(line.strip()) > 0:
            return True
        else:
            False


def containsAny(line, letters):
    """Check if any of the letters are in the line"""
    for letter in letters:
        if letter in line:
            return True
    return False

def containsOnly(line, letters):
    """Check if the line only contains these letters"""
    for c in line:
        if c.isalnum(): # if character is alphanumeric
            if c in letters:
                continue
            else: # character not found in letters
                return False
        else: # ignore non-alphanumeric characters
            continue

    return True

        
# characters that are used or not used in guitar chords
chords = "ABCDEFGminajsugd123456789"
notChords = "HJKLOPQRTVWXYZ"


if __name__ == "__main__":
    # if run from command line, convert first argument
    if len(sys.argv) is 1:
        raise IOError("Please supply a filename as argument")
    c = ChordConverter()
    c.convert(sys.argv[1])
