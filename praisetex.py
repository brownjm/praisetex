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

"""praisetex.py - Program used to generate presentation slides and chords 
sheets"""

import os
import subprocess
from collections import deque
try:
    # if using python2.x
    from Tkinter import *
    import tkFileDialog
except ImportError:
    try:
        # if using python3.x
        from tkinter import *
        import tkinter.filedialog as tkFileDialog
    except ImportError:
        raise ImportError("Tkinter for Python is not installed")

import chord_sheet_converter as csc

class PraiseTexGUI(object):
    """Graphical interface for selecting songs and compiling them"""
    def __init__(self, root, songdir="songs"):
        # data
        self.songdir = songdir
        self.songs = []

        # dimensions for layout
        #window_width = 600
        #window_height = 480
        button_width = 6
        button_padx = "2m"
        button_pady = "1m"
        frame_padx = "3m"
        frame_pady = "2m"
        label_padx = "3m"
        label_pady = "2m"
        listbox_width = 30
        listbox_height = 20
        label_font = ("Arial", 14)

        # window properties
        root.title("praiseTex")
        # set initial size of window
        #root.geometry("{0}x{1}".format(window_width, window_height))

        # menu
        menubar = Menu(root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open Directory", command=self.openDirectory)
        filemenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        toolmenu = Menu(menubar, tearoff=0)
        toolmenu.add_command(label="Convert Chord Sheet", command=self.convert)
        menubar.add_cascade(label="Tools", menu=toolmenu)
        root.config(menu=menubar)

        # left section
        self.songsToCompileTitle = Label(root, text="Songs to Compile", 
                                         font=label_font,
                                         padx=label_padx, pady=label_pady)
        self.songsToCompileTitle.grid(row=0, column=0)
        self.songsToCompileFrame = Frame(root)
        self.songsToCompileFrame.grid(row=1, column=0, 
                                      padx=frame_padx, pady=frame_pady)
        self.songsToCompileScroll = Scrollbar(self.songsToCompileFrame,
                                              orient=VERTICAL)
        self.songsToCompile = Listbox(self.songsToCompileFrame, 
                                      width=listbox_width, 
                                      height=listbox_height, 
                                      selectmode=EXTENDED,
                                      yscrollcommand=self.songsToCompileScroll.set)
        self.songsToCompileScroll.config(command=self.songsToCompile.yview)
        self.songsToCompileScroll.pack(side=RIGHT, fill=Y)
        self.songsToCompile.pack()
        
        self.compileButtonFrame = Frame(root)
        self.compileButtonFrame.grid(row=2, column=0)
        self.chordsButton = Button(self.compileButtonFrame, 
                                   text="Chords", 
                                   command=self.compileChords)
        self.chordsButton.pack(side=LEFT, padx=button_padx, pady=button_pady)
        self.slidesButton = Button(self.compileButtonFrame, 
                                   text="Slides", 
                                   command=self.compileSlides)
        self.slidesButton.pack(side=RIGHT, padx=button_padx, pady=button_pady)

        # middle section
        self.addRemoveButtonFrame = Frame(root)
        self.addRemoveButtonFrame.grid(row=1, column=1)
        self.addSongButton = Button(self.addRemoveButtonFrame,
                                    text="<<", 
                                    command=self.addSong)
        self.addSongButton.pack(side=TOP, padx=button_padx, pady=button_pady)
        self.removeSongButton = Button(self.addRemoveButtonFrame, 
                                       text=">>", 
                                       command=self.removeSong)
        self.removeSongButton.pack(side=BOTTOM)

        # right section
        self.availableSongsTitle = Label(root, 
                                         text="Available Songs",
                                         font=label_font,
                                         padx=label_padx, 
                                         pady=label_pady)
        self.availableSongsTitle.grid(row=0, column=2)
        self.availableSongsFrame = Frame(root)
        self.availableSongsFrame.grid(row=1, column=2,
                                      padx=frame_padx, pady=frame_pady)
        self.availableSongsScroll = Scrollbar(self.availableSongsFrame, 
                                              orient=VERTICAL)
        self.availableSongs = Listbox(self.availableSongsFrame, 
                                      width=listbox_width, 
                                      height=listbox_height, 
                                      selectmode=EXTENDED, 
                                      yscrollcommand=self.availableSongsScroll.set)
        self.availableSongsScroll.config(command=self.availableSongs.yview)
        self.availableSongsScroll.pack(side=RIGHT, fill=Y)
        self.availableSongs.pack()
        self.button = Button(root, 
                             text="Refresh",  
                             command=self.refreshSonglist)
        self.button.grid(row=2, column=2)

        # status bar
        self.status = Label(root, text="Ready", padx="1m")
        self.status.grid(row=3, column=0, columnspan=3, sticky=W)

        self.refreshSonglist()

    def refreshSonglist(self):
        """Sync up the filenames in songlist with files in directory"""
        # clear song list
        self.availableSongs.delete(0, END)

        # add song files
        self.songs = os.listdir(self.songdir)
        # filter out song files ending with tex file extension
        self.songs = [song for song in self.songs if song.endswith('tex') or song.endswith('_')]
        self.songs.sort() # alphabetize
        for song in self.songs:
            self.availableSongs.insert(END, song)
        self.updateStatus("{0} songs found in directory {1}".format(len(self.songs), self.songdir))

    def openDirectory(self):
        """Selects directory for songs"""
        dirname = tkFileDialog.askdirectory(parent=root, initialdir=self.songdir, title='Please select a directory')
        if len(dirname) > 0:
            self.songdir = dirname

    def addSong(self):
        """Add song to compile list"""
        songindexes = self.availableSongs.curselection()
        for index in songindexes:
            self.songsToCompile.insert(END, self.availableSongs.get(index))

        self.updateStatus("{0} songs added".format(len(songindexes)))

    def removeSong(self):
        """Remove song from compile list"""
        songindexes = list(self.songsToCompile.curselection())
        songindexes.reverse()
        for index in songindexes:
            self.songsToCompile.delete(index)
            
        self.updateStatus("{0} songs removed".format(len(songindexes)))

    def compileChords(self):
        """Compile a chord sheet from selected songs"""
        self.updateStatus("Reading file latex/chords.tex")
        # read in chords template
        with open("latex/chords.tex", "r") as f:
            lines = f.readlines()
        
        # find line number ranges for where \input{song.tex} should be
        begin = lines.index("\\begin{multicols}{2}\n")+1
        end = lines.index("\\end{multicols}\n")
        top = lines[:begin]
        bottom = lines[end:]
        
        # create temporary document containing songs
        ctmp = []
        ctmp.extend(top)
        ctmp.append(self.createSongString())
        ctmp.extend(bottom)
        with open("ctmp.tex", "w") as f:
            f.writelines(ctmp)

        # compile document
        self.updateStatus("Compiling songs")
        error = subprocess.call(["pdflatex", "-halt-on-error", "ctmp.tex"])
        if error:
            self.updateStatus("pdflatex has failed")
        else:
            os.rename("ctmp.pdf", "chords.pdf")
            self.updateStatus("Compiled chords.pdf")

        # remove temporary files
        fnames = os.listdir('.')
        for f in fnames:
            if "ctmp" in f:
                os.remove(f)

    def compileSlides(self):
        """Compile slides from selected songs"""
        self.updateStatus("Reading file latex/slides.tex")
        # read in chords template
        with open("latex/slides.tex", "r") as f:
            lines = f.readlines()
        
        # find line number ranges for where \input{song.tex} should be
        begin = lines.index("\\begin{document}\n")+1
        end = lines.index("\\end{document}\n")
        top = lines[:begin]
        bottom = lines[end:]
        
        # create temporary document containing songs
        stmp = []
        stmp.extend(top)
        stmp.append(self.createSongString())
        stmp.extend(bottom)
        with open("stmp.tex", "w") as f:
            f.writelines(stmp)

        # compile document
        self.updateStatus("Compiling songs")
        #error = subprocess.call(["pdflatex", "-halt-on-error", "stmp.tex"])
        error = subprocess.call(["pdflatex", "-halt-on-error",  "\\pdfminorversion=4", "\\input{stmp.tex}"])
        if error:
            self.updateStatus("pdflatex has failed")
        else:
            os.rename("stmp.pdf", "slides.pdf")
            self.updateStatus("Compiled slides.pdf")

        # remove temporary files
        fnames = os.listdir('.')
        for f in fnames:
            if "stmp" in f:
                os.remove(f)
        self.updateStatus("Compiled slides.pdf")

    def createSongString(self):
        """Construct latex \input strings containing selected songs"""
        songList = self.songsToCompile.get(0, END)
        folder = os.path.join(self.songdir, '')                
        return "".join(["\input{{{0}{1}}}\n".format(folder, song) for song in songList])

    def updateStatus(self, message):
        """Update the status bar"""
        self.status.config(text=message)

    def convert(self):
        filename = tkFileDialog.askopenfilename()
        if len(filename) > 0:
            converter = csc.ChordConverter()
            converter.convert(filename)
            self.updateStatus("Wrote file: {}".format(filename + ".tex"))


class Song(object):
    """Representing a song file."""
    def __init__(self, filename):
        self.filename = filename
        with open(filename, 'r') as f:
            self.text = f.readlines()

    def write(self, filename):
        if filename == self.filename:
            raise NameError("Cannot overwrite original file '{}', please choose another filename.".format(self.filename))
        with open(filename, 'w') as f:
            for line in self.text:
                f.write(line)


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


if __name__ == '__main__':
    root = Tk()
    gui = PraiseTexGUI(root)
    root.mainloop()
