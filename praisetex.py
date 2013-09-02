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

"""praisetex.py - Program used to generate presentation slides and chords 
sheets"""

import sys
import os
from collections import deque
import argparse

import core
import song
import gui
#import chord_sheet_converter as csc

# get praisetex folders's absolute path
praisetex_dir = os.path.dirname(os.path.abspath(__file__))

def runGUI():
    app = gui.PraiseTexGUI(os.path.join(praisetex_dir, "songs"))
    app.run()

# def convert(filename):
#     for filename in args.filename:
#         print("Converting chord sheet: {}".format(filename))
#         converter = csc.ChordConverter()
#         try:
#             converter.convert(filename)
#         except IOError as ioe:
#             print(ioe)
#             sys.exit()

# def transpose(filenames, numHalfSteps):
#     if numHalfSteps != 0:
#         for filename in filenames:
#             print("Transposing {} by {} half steps".format(filename, numHalfSteps))
#             s = core.Song(filename)
#             s.transpose(numHalfSteps)
#             newfilename = '{0}{1:+2d}'.format(filename, numHalfSteps)
#             s.write(newfilename)
#             print("Wrote new file: {}".format(newfilename))


def chords(filename):
    if len(filename) > 0:
        print("Creating chords from: {}".format(args.filename))
        songList = [f for f in filename]
        praisetex = core.PraiseTex()
        praisetex.refreshSongList()
        index = 0
        for songtitle in songList:
            praisetex.addSong(index, songtitle)
            index += 1
        error = praisetex.compileChords()
        if error:
            print("pdflatex has failed")
        else:
            print("Compiled chords.pdf")

def slides(filename):
    if len(filename) > 0:
        print("Creating slides from: {}".format(args.filename))
        songList = [song.Song(f).attributes["title"] for f in filename]
        praisetex = core.PraiseTex()
        praisetex.refreshSongList()
        index = 0
        for songtitle in songList:
            praisetex.addSong(index, songtitle)
            index += 1
        error = praisetex.compileSlides()
        if error:
            print("pdflatex has failed")
        else:
            print("Compiled slides.pdf")

def getParser():
    parser = argparse.ArgumentParser(description='praiseTex: program for creating guitar chordsheets and presentation slides.')

    # options compiling multiple song files
    parser.add_argument(action='store', dest='filename', nargs='*')
    parser.add_argument('-c', '--chords', action='store_true', default=False, 
                        help='create chord sheets from provided song files')
    parser.add_argument('-s', '--slides', action='store_true', default=False, 
                        help='create presentation slides from provided song files')

    # options for altering song files
    # parser.add_argument('--convert', action='store_true', default=False, 
    #                     help='convert guitar chord sheet into praiseTex song file')
    # parser.add_argument('--transpose', action='store', type=int, metavar='N',
    #                     help='transpose song file by number of half steps')
    return parser



if __name__ == '__main__':
    # command line parsing and handling
    parser = getParser()
    args = parser.parse_args()


    # if args.convert: # converting chord sheet to praisetex song file
    #     convert(args.filename)

    # elif args.transpose is not None: # transposing song
    #     transpose(args.filename, args.transpose)
        
    # elif args.chords or args.slides: # creating chords or slides
    if args.chords or args.slides: # creating chords or slides
        if args.chords:
            chords(args.filename)

        if args.slides:
            slides(args.filename)

    else:
        runGUI()

