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

"""gui.py - A tkinter frontend to the praiseTex program"""

import sys

if sys.version_info[:2] == (2, 7): # if using python2.7+
    try:
        from Tkinter import Tk, Menu, Frame, Label, Listbox, Button, \
            Scrollbar, VERTICAL, EXTENDED, LEFT, RIGHT, TOP, BOTTOM, \
            Y, W, END
        import tkFileDialog as filedialog
    except ImportError:
        raise ImportError("Tkinter for Python is not installed")

elif sys.version_info[0] == 3:
    try: # if using python3.x+
        from tkinter import Tk, Menu, Frame, Label, Listbox, Button, \
            Scrollbar, VERTICAL, EXTENDED, LEFT, RIGHT, TOP, BOTTOM, \
            Y, W, END
        from tkinter import filedialog
        from tkinter.ttk import Scrollbar
    except ImportError:
        raise ImportError("Tkinter for Python is not installed")

else:
    raise "Must use Python version 2.7+ or 3.x+"

from core import PraiseTex


## scaling application
# class App:
#     def __init__(self):
#         root=tk.Tk()
#         # create a custom font
#         self.customFont = tkFont.Font(family="Helvetica", size=12)

#         # create a couple widgets that use that font
#         buttonframe = tk.Frame()
#         label = tk.Label(root, text="Hello, world", font=self.customFont)
#         text = tk.Text(root, width=20, height=2, font=self.customFont)
#         buttonframe.pack(side="top", fill="x")
#         label.pack()
#         text.pack()
#         text.insert("end","press +/- buttons to change\nfont size")

#         # create buttons to adjust the font
#         bigger = tk.Button(root, text="+", command=self.OnBigger)
#         smaller = tk.Button(root, text="-", command=self.OnSmaller)
#         bigger.pack(in_=buttonframe, side="left")
#         smaller.pack(in_=buttonframe, side="left")

#         root.mainloop()

#     def OnBigger(self):
#         '''Make the font 2 points bigger'''
#         size = self.customFont['size']
#         self.customFont.configure(size=size+2)

#     def OnSmaller(self):
#         '''Make the font 2 points smaller'''
#         size = self.customFont['size']
#         self.customFont.configure(size=size-2)

# app=App()


class PraiseTexGUI(object):
    """Graphical interface for selecting songs and compiling them"""
    def __init__(self, songdir="songs"):
        # data
        self.songs = []
        self.praisetex = PraiseTex(songdir)
        self.root = Tk()
        
        # screen_width = self.root.winfo_screenwidth()
        # screen_height = self.root.winfo_screenheight()
        # print(screen_width, screen_height)
        # avg_screen_width = 1280
        # scale_dpi = screen_width / avg_screen_width
        # print('DPI: ', self.root.winfo_fpixels('1i'))
        # self.root.tk.call('tk', 'scaling', '-displayof', '.', scale_dpi)

        # dimensions for layout
        # window_width = 600
        # window_height = 480
        button_width = 6
        button_padx = "2m"
        button_pady = "1m"
        frame_padx = "3m"
        frame_pady = "2m"
        label_padx = "3m"
        label_pady = "2m"
        listbox_width = 30
        listbox_height = 20
        frame_title_font = ("TkDefaultFont", 14)
        text_font = ("TkDefaultFont", 12)
        menu_font = ("TkDefaultFont", 12)
        button_font = ("TkDefaultFont", 12)

        # window properties
        self.root.title("praiseTex")
        self.root.option_add("*Font", ("TkDefaultFont", 12))
        # set initial size of window
        #self.root.geometry("{0}x{1}".format(window_width, window_height))

        # menu
        menubar = Menu(self.root)
        menubar.tk.call('tk', 'scaling', 2.5)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open Directory", command=self.openDirectory)
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        # toolmenu = Menu(menubar, tearoff=0)
        # toolmenu.add_command(label="Convert Chord Sheet", command=self.convert)
        # menubar.add_cascade(label="Tools", menu=toolmenu)
        self.root.config(menu=menubar)

        # left section
        self.songsToCompileTitle = Label(self.root, text="Songs to Compile", 
                                         font=frame_title_font,
                                         padx=label_padx, pady=label_pady)
        self.songsToCompileTitle.grid(row=0, column=0)
        self.songsToCompileFrame = Frame(self.root)
        self.songsToCompileFrame.grid(row=1, column=0, 
                                      padx=frame_padx, pady=frame_pady)
        self.songsToCompileScroll = Scrollbar(self.songsToCompileFrame,
                                              orient=VERTICAL)
        self.songsToCompile = Listbox(self.songsToCompileFrame, 
                                      width=listbox_width, 
                                      height=listbox_height, 
                                      selectmode=EXTENDED,
                                      yscrollcommand=self.songsToCompileScroll.set,
                                      exportselection=0,
                                      font=text_font)
        self.songsToCompileScroll.config(command=self.songsToCompile.yview)
        self.songsToCompileScroll.pack(side=RIGHT, fill=Y)
        self.songsToCompile.pack()

        self.compileButtonFrame = Frame(self.root)
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
        self.addRemoveButtonFrame = Frame(self.root)
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
        self.availableSongsTitle = Label(self.root, 
                                         text="Available Songs",
                                         font=frame_title_font,
                                         padx=label_padx, 
                                         pady=label_pady)
        self.availableSongsTitle.grid(row=0, column=2)
        self.availableSongsFrame = Frame(self.root)
        self.availableSongsFrame.grid(row=1, column=2,
                                      padx=frame_padx, pady=frame_pady)
        self.availableSongsScroll = Scrollbar(self.availableSongsFrame, 
                                              orient=VERTICAL)
        self.availableSongs = Listbox(self.availableSongsFrame, 
                                      width=listbox_width, 
                                      height=listbox_height, 
                                      selectmode=EXTENDED, 
                                      yscrollcommand=self.availableSongsScroll.set,
                                      exportselection=0)
        self.availableSongsScroll.config(command=self.availableSongs.yview)
        self.availableSongsScroll.pack(side=RIGHT, fill=Y)
        self.availableSongs.pack()

        self.button = Button(self.root, 
                             text="Refresh",  
                             command=self.refreshSongList)
        self.button.grid(row=2, column=2)

        # status bar
        self.status = Label(self.root, text="Ready", padx="1m")
        self.status.grid(row=3, column=0, columnspan=3, sticky=W)

        self.refreshSongList()

    def run(self):
        """Start event loop of GUI"""
        self.root.mainloop()

    def refreshSongList(self):
        """Sync up the filenames in songlist with files in directory"""
        # clear song list
        self.availableSongs.delete(0, END)

        # add song files
        self.songs = self.praisetex.refreshSongList()
        for song in self.songs:
            self.availableSongs.insert(END, song)
        self.updateStatus("{0} songs found in directory {1}".format(len(self.songs), self.praisetex.getSongDirectory()))

    def openDirectory(self):
        """Selects directory for songs"""
        dirname = filedialog.askdirectory(parent=self.root, initialdir=self.praisetex.getSongDirectory(), title='Please select a directory')
        if len(dirname) > 0:
            self.praisetex.setSongDirectory(dirname)
            self.updateStatus("Song directory set to {0}".format(dirname))

    def addSong(self):
        """Add song to compile list"""
        # TODO: remove all code that manipulates the listbox and praisetex 
        # list simultaneously. Rewrite using MVC scheme, where after each 
        # transaction the listbox (view) is updated.
        selectedSongs = self.availableSongs.curselection()

        # get index of where to insert selected songs
        insertIndex = self.songsToCompile.curselection()
        if len(insertIndex) > 0:
            insertIndex = int(insertIndex[0]) # convert to integer
        else:
            insertIndex = -1 # song should be appended


        if len(selectedSongs) == 0: # do nothing
            pass
            
        elif len(selectedSongs) == 1: # insert the one song
            song = selectedSongs[0]
            songtitle = self.availableSongs.get(song)
            if insertIndex == -1:
                end = len(self.praisetex.compile)
                self.praisetex.addSong(end, songtitle)
                self.songsToCompile.insert(END, songtitle)
            else:
                self.praisetex.addSong(insertIndex+1, songtitle)
                self.songsToCompile.insert(insertIndex+1, songtitle)
            
        else: # more than one song  
            songList = [self.availableSongs.get(song) for song in selectedSongs]
            if insertIndex != -1:
                songList.reverse()
                for songtitle in songList:
                    self.praisetex.addSong(insertIndex+1, songtitle)
                    self.songsToCompile.insert(insertIndex+1, songtitle)
            else: # add songs to the end
                for songtitle in songList:
                    end = len(self.praisetex.compile)
                    self.praisetex.addSong(end, songtitle)
                    self.songsToCompile.insert(END, songtitle)
       

        #print "Index: ", insertIndex
        #print [song.title for song in self.praisetex.compile]
        self.updateStatus("{0} songs added".format(len(selectedSongs)))



        """
        for song in selectedSongs:
            songtitle = self.availableSongs.get(song)
            # curselection returns an empty tuple if no selection is made
            insertIndex = self.songsToCompile.curselection()
            if len(insertIndex) > 0:
                insertIndex = int(insertIndex[0])
                self.praisetex.addSong(insertIndex+1+offset, songtitle)
                self.songsToCompile.insert(insertIndex+1+offset, songtitle)
                offset += 1
            else: # insert songs at the end
                insertIndex = END
                self.praisetex.addSong(-1, songtitle)
                self.songsToCompile.insert(insertIndex, songtitle)
         """         



    def removeSong(self):
        """Remove song from compile list"""
        songindexes = list(self.songsToCompile.curselection())
        songindexes.reverse()
        for index in songindexes:
            self.praisetex.removeSong(index)
            self.songsToCompile.delete(index)
            
        self.updateStatus("{0} songs removed".format(len(songindexes)))

    def compileChords(self):
        """Compile a chord sheet from selected songs"""
        self.updateStatus("Compiling Songs")
        error = self.praisetex.compileChords()
        if error:
            self.updateStatus("pdflatex has failed")
        else:
            self.updateStatus("Compiled chords.pdf")

    def compileSlides(self):
        """Compile slides from selected songs"""
        self.updateStatus("Compiling Songs")
        error = self.praisetex.compileSlides()
        if error:
            self.updateStatus("pdflatex has failed")
        else:
            self.updateStatus("Compiled slides.pdf")

    def updateStatus(self, message):
        """Update the status bar"""
        self.status.config(text=message)

    # def convert(self):
    #     filename = filedialog.askopenfilename()
    #     if len(filename) > 0:
    #         self.praisetex.convert(filename)
    #         self.updateStatus("Wrote file: {}".format(filename + ".tex"))


if __name__ == '__main__':
    p = PraiseTexGUI()
    p.run()
