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

"""core.py - Provides core classes and function for praiseTex program"""

from collections import deque
import re


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
        chordstr = re.split(r'(/| |\d|m|M|sus|maj)', chord) # split by /, space and number
        newChordList = []
        for chord in chordstr:
            if chord in self.chords:
                chord = self.chordDict[chord]
            newChordList.append(chord)
        return ''.join(newChordList)


class Song(object):
    """Representing a song file"""
    def __init__(self, filename, commands=commandDict):
        self.filename = filename
        self.commands = commands

        with open(filename, 'r') as f:
            self.text = f.read()

        self.getAttributes()

    def write(self, filename):
        """Write the song to a file (protects against overwriting original)"""
        if filename == self.filename:
            raise NameError("Cannot overwrite original file '{}', please choose another filename.".format(self.filename))
        with open(filename, 'w') as f:
            for line in self.text:
                f.write(line)

    def getAttributes(self):
        for attr, latexcommand in self.commands.items():
            m = re.search(r'\\' + latexcommand + r'\{([^{]*)\}', self.text)
            if m is not None:
                setattr(self, attr, m.groups()[0])

    def transpose(self, numHalfSteps):
        """Transpose each chord within song by specified number of half steps"""
        cm = ChordMap(numHalfSteps)
        stringList = []
        text = self.text
        
        match = re.search(chordCommand, text)
        while match is not None:
            before = text[:match.start()] # up to chord
            chord = text[match.start():match.end()] # chord       
            stringList.append(before)
 
            # find which command matched and grab actual chord
            ch, left, line = match.groups()
            if ch is not None:
                command = '\chord{{{}}}'
                letter = ch
            elif left is not None:
                command = '\chordleft{{{}}}'
                letter = left
            elif line is not None:
                command = '\chordline{{{}}}'
                letter = line
            else:
                raise 'No chord match found'
            
            newletter = cm.transpose(letter) # transposition
            #print(newletter, command, before)
            stringList.append(command.format(newletter)) # add new chord
            text = text[match.end():] # focus on remaining string
            match = re.search(chordCommand, text)
            match = 1

        stringList.append(text) # add final string
        self.text = ''.join(stringList)

    def locateCommands(self):
        """Build a list of songs commands and their locations"""
        with open(self.filename, 'r') as f:
            text = f.readlines()

        linenum = 0
        commands = []

        for line in text:
            # matches latex command pattern: \command{argument}
            matches = re.finditer(latexCommandPattern, line)
            for match in matches:
                command, arg = match.groups()
                span = match.regs[-1]
                commands.append((command, arg, linenum, span))
            linenum += 1

        return commands


class PraiseTex(object):
    """Class for producing chords and slides from song files"""
    def __init__(self, songdir="songs"):
        self.songdir = songdir
        self.songs = {}
        self.compile = []

    def refreshSongList(self):
        """Reload available songs found in songs directory"""
        self.songs.clear()
        filenames = os.listdir(self.songdir)
        # filter song filenames ending with tex or underscore
        filenames = [song for song in filenames if song.endswith('tex') or song.endswith('_')]
        songs = [Song(os.path.join(self.songdir, fn)) for fn in filenames]
        self.songs = dict([(song.title, song) for s in songs])
        return self.songs.keys()

    def setSongDirectory(self, directory):
        """Set directory containing song files"""
        if len(directory) > 0:
            self.songdir = directory

    def addSong(self, index):
        if index < len(self.filenames):
            n = self.filenames.index()
