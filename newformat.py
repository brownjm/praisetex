"""Convert latex song files to new plain text format"""

import sys
import re

chord_pattern = re.compile(r'\\(\w+)\{([^{]*)\}')

def convert(song):
    """Convert old song file format (latex) into new format (plain text)"""
    newsong = []
    for line in song:
        if has_chords(line):
            newlines = split_line(line)
            newsong.extend(newlines)
        else:
            newsong.append(line)

    return newsong


def has_chords(line):
    """Searches line to see if chords exists"""
    if r"\chord" in line:
        return True
    else:
        return False
    
    
def split_line(lyrics, chordline=''):
    """Removes inline chord commands and place them above the lyrics"""
    if not has_chords(lyrics): # nothing left to do
        return lyrics, chordline

    begin, end, command, chord = find_next_chord(lyrics)
    lyrics = remove_chord(lyrics, begin, end)
    chordline = add_chord(chordline, begin)

    return chordline, lyrics

def find_next_chord(line):
    """Finds the first chord in the line"""
    match = re.search(chord_pattern, line)
    begin, end = match.span()
    command, chord = match.groups()
    return begin, end, command, chord

def remove_chord(lyrics, begin, end):
    return lyrics[:begin] + lyrics[end:]

def add_chord(chordline, begin):
    return chordline.rjust



if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise IOError("Please provide an input file\n")

    filename = sys.argv[1]
    with open(filename, 'r') as f:
        lines = f.readlines()
        newlines = convert(lines)
