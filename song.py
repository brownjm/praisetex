"""New song class to work with a plain text song file format"""

import os
import re

chord_regex = re.compile("[A-G][1-9#bminajsugd]*[/]*[A-G]*[1-9#bminajsugd]*")
valid_chords = "ABCDEFGb#minajsugd123456789"
not_chords = "HJKLOPQRTVWXYZ\n"


class Chord(object):
    """Represents a single chord within a song file"""
    def __init__(self, chord):
        self.text = chord
    def __repr__(self):
        return "Chord({})".format(self.text)

class Chordline(object):
    """Represents multiple chords that are on a separate line"""
    def __init__(self, chords):
        self.text = chords
    def __repr__(self):
        return "Chordline({})".format(self.text)

class Text(object):
    """Represents plain text, such as lyrics, within a song file"""
    def __init__(self, text):
        self.text = text
    def __repr__(self):
        return "Text({})".format(self.text)


def combine(chord_line, lyrics):
    """Combines a line of chords with its associated lyrics"""
    # make sure the lyrics line is long enough to hold chords
    if(len(chord_line) > len(lyrics)):
        lyrics = lyrics.ljust(len(chord_line))

    # find valid chords
    matches = chord_regex.finditer(chord_line)
    # list of (location, chord)
    chords = list(zip([match.start() for match in matches],
                      chord_line.split()))
    # insert chords in verse order since insertion shifts positions of subsequent chords
    combined = []
    chords.reverse()
    for chord in chords:
        loc, ch = chord
        combined.append(Text(lyrics[loc:]))
        combined.append(Chord(ch))
        lyrics = lyrics[:loc]

    if len(lyrics) > 0: # handle any leftover text before first chord
        combined.append(Text(lyrics))

    combined.reverse()
    return combined

def is_chord_line(line):
    """Checks if the line contains chords"""
    if contains_only(line, valid_chords) and not contains_any(line, not_chords):
        return True
    else:
        return False



def find_commands(text):
    """Returns a list of line numbers which contain a colon, representing a command"""
    line_numbers = []
    num = 0
    for line in text:
        if ":" in line:
            line_numbers.append(num)
        num += 1
            
    return line_numbers

def contains_any(line, letters):
    """Check if any of the letters are in the line"""
    for letter in letters:
        if letter in line:
            return True
    return False

def contains_only(line, letters):
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

if __name__ == '__main__':
    s = Song('songs/10000Reasons.txt')
    c = s.attributes['chorus 1']
