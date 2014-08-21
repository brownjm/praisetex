#!/usr/bin/python
#    praiseTex - simple set of programs for creating praise music material,
#    such as guitar chord sheets and presentation slides
#
#    Copyright (C) 2013 Jeffrey M Brown
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

"""core.py - Provides core classes and function for praiseTex program"""

from collections import deque
import re
import os
import subprocess
import song
import latex
import parser

# regex pattern for any latex command with the form: \command{arg}
latexCommandPattern = r'\\(\w+)\{([^{]*)\}'

# maps song class attribute to latex command name
commandDict = {'title':'songtitle',
               'author':'by',
               'comment':'comment'}

# regex pattern for three latex chord commands
chordCommand = r'\\chord\{([^{}]*)\}|\\chordleft\{([^{}]*)\}|\\chordline\{([^{}]*)\}'


class ChordMap(object):
    """A dictionary of chords used for transposition"""
    def __init__(self, nHalfSteps, preferSharps=True):
        self.halfsteps = int(nHalfSteps)
        if preferSharps:
            self.chords = ['A', 'A\\#', 'B', 'C', 'C\\#', 'D', 'D\\#', 'E',
                           'F', 'F\\#', 'G', 'G\\#']
        else:
            self.chords = ['A', 'B$\\flat$', 'B', 'C', 'D$\\flat$', 'D',
                           'E$\\flat$', 'E', 'F', 'G$\\flat$', 'G',
                           'A$\\flat$']

        # map the original chords to the new transposed ones
        original = deque(self.chords)
        transposed = deque(self.chords)
        transposed.rotate(-nHalfSteps) # shift by number of half steps
        self.chordDict = dict(zip(original, transposed))

    def __getitem__(self, chord):
        return self.chordDict[chord]

    def transpose(self, chord):
        # split by /, space and number
        chordstr = re.split(r'(/| |\d|m|M|sus|maj)', chord) 
        newChordList = []
        for chord in chordstr:
            if chord in self.chords:
                chord = self.chordDict[chord]
            newChordList.append(chord)
        return ''.join(newChordList)



class PraiseTex(object):
    """Class for producing chords and slides from song files"""
    def __init__(self, songdir="songs"):
        self.songdir = songdir
        #self.songs = {}
        self.songs = []
        self.compile = []

    def refreshSongList(self):
        """Reload the song found in 'songs' directory"""
        del self.songs[:] # delete contents of song list
        filenames = os.listdir(self.songdir)
        # keep only song filenames ending with 'txt'
        songlist = [fn for fn in filenames if fn.endswith('.txt') or fn.endswith('___')]
        songlist.sort() # alphabetize
        return songlist

    def setSongDirectory(self, directory):
        """Set directory containing song files"""
        if len(directory) > 0:
            self.songdir = directory

    def getSongDirectory(self):
        """Return current song directory"""
        return self.songdir

    def addSong(self, index, songtitle):
        """Add song to compile list"""
        index = int(index)
        #song = self.songs[songtitle]
        #self.compile.append(song)
        self.compile.insert(index, songtitle)

    def removeSong(self, index):
        """Remove song from compile list"""
        index = int(index)
        if index < len(self.compile):
            self.compile.pop(index)

    def compileChords(self):
        """Compile a chord sheet from selected songs"""
        # read in chords template
        with open("latex/chords.tex", "r") as f:
            lines = f.readlines()

        # find line number ranges where \input{song.tex} should be
        begin = lines.index("\\begin{multicols}{2}\n") + 1
        end = lines.index("\\end{multicols}\n")
        top = lines[:begin]
        bottom = lines[end:]

        # create text from template and songs to pass to pdflatex
        ctmp = []
        ctmp.extend(top)
        # count = 0
        for song in self.compile:
            fullpathfilename = os.path.join(self.songdir, song)
            songtext = parser.compile_chords(fullpathfilename)
            ctmp.append(songtext)
            # with open('tmp/{}.tex'.format(song.replace('.txt', '')), 'w') as f:
            #     f.writelines(top)
            #     f.writelines(songtext)
            #     f.writelines(bottom)
            # count += 1
            
        ctmp.extend(bottom)
        with open("ctmp.tex", "w") as f:
            f.writelines(ctmp)

        # compile document
        error = subprocess.call(["pdflatex", "-halt-on-error", "\\pdfminorversion=4", "\\input{ctmp.tex}"])

        if not error:
            os.rename("ctmp.pdf", "chords.pdf")

        # remove temporary files
        fnames = os.listdir('.')
        for f in fnames:
            if "ctmp" in f:
                os.remove(f)

        return error

    def compileSlides(self):
        """Compile slides from selected songs"""
        # read in chords template
        with open("latex/slides.tex", "r") as f:
            lines = f.readlines()

        # find line number ranges where \input{song.tex} should be
        begin = lines.index("\\begin{document}\n") + 1
        end = lines.index("\\end{document}\n")
        top = lines[:begin]
        bottom = lines[end:]

        # create text from template and songs to pass to pdflatex
        stmp = []
        stmp.extend(top)
        for song in self.compile:
            fullpathfilename = os.path.join(self.songdir, song)
            songtext = parser.compile_slides(fullpathfilename)
            stmp.append(songtext)

        stmp.extend(bottom)
        with open("stmp.tex", "w") as f:
            f.writelines(stmp)

        # compile document
        error = subprocess.call(["pdflatex", "-halt-on-error",  "\\pdfminorversion=4", "\\input{stmp.tex}"])
        
        if not error:
            os.rename("stmp.pdf", "slides.pdf")

        # remove temporary files
        fnames = os.listdir('.')
        for f in fnames:
            if "stmp" in f:
                os.remove(f)

        return error


if __name__ == '__main__':
    p = PraiseTex()
