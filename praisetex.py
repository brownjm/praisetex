"""praisetex.py - Program used to generate presentation slides and chords 
sheets"""

import sys
import os
from collections import deque
import argparse

import core
import gui

# get praisetex folders's absolute path
praisetex_dir = os.path.dirname(os.path.abspath(__file__))

def runGUI():
    app = gui.PraiseTexGUI(os.path.join(praisetex_dir, "songs"))
    app.run()


def chords(filename):
    if len(filename) > 0:
        print("Creating chords from: {}".format(args.filename))
        songList = [os.path.basename(f) for f in filename]
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
        songList = [os.path.basename(f) for f in filename]
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
    # parser.add_argument('--transpose', action='store', type=int, metavar='N',
    #                     help='transpose song file by number of half steps')
    return parser



if __name__ == '__main__':
    # command line parsing and handling
    parser = getParser()
    args = parser.parse_args()
        
    if args.chords or args.slides: # creating chords or slides
        if args.chords:
            chords(args.filename)

        if args.slides:
            slides(args.filename)

    # elif args.transpose is not None: # transposing song
    #     transpose(args.filename, args.transpose)

    else:
        runGUI()

