"""New song class to work with a plain text song file format"""

import os
import re

chord_regex = re.compile("[A-G][1-9#bminajsugd]*[/]*[A-G]*[1-9#bminajsugd]*")
valid_chords = "ABCDEFGminajsugd123456789"
not_chords = "HJKLOPQRTVWXYZ"
paren_regex = re.compile("\((.+)\)")

class Chord(object):
    """Represents a single chord within a song file"""
    def __init__(self, chord):
        self.text = chord

class Chordline(object):
    """Represents multiple chords that are on a separate line"""
    def __init__(self, chords):
        self.text = chords

class Text(object):
    """Represents plain text, such as lyrics, within a song file"""
    def __init__(self, text):
        self.text = text

class Parentheses(object):
    """Represents text surrounded in parentheses, which in a song file would tell the read to go to a specified stanza"""
    def __init__(self, text):
        match = re.search(paren_regex, text.strip())
        if match is not None:
            self.text = match.groups()[0]
        else:
            raise ValueError("Parentheses not found")

class KeyValuePair(object):
    """Colon separated key-value pair"""
    def __init__(self, line):
        #print("Found key-value: {}\n".format(line))
        first, second = line.split(':')
        self.command = first.strip().lower()
        self.value = second.strip()


class Stanza(object):
    """Represents a block of lyrics and chords"""
    def __init__(self, text):
        #print("Found Stanza: {}\n".format(text))
        command_line = text[0]
        n = command_line.index(":")
        self.command = command_line[:n]
        self.type = self.command.split()[0].lower()
        self.raw_lines = text[1:]

        self._parse()

    def _parse(self):
        # lines is a list of the text lines in the song file
        # each line in lines is also a list of chords and text objects
        self.lines = []
        num_lines = len(self.raw_lines)
        n = 0
        while n < num_lines:
            line = self.raw_lines[n]
            chords = is_chord_line(line)
            
            # handle special case of dangling last line
            if n == num_lines-1: # last line
                if chords:
                    # append a list of chordline to match
                    self.lines.append([Chordline(line)])
                else:
                    self.lines.append([Text(line)])
                break

            next_line = self.raw_lines[n+1]
            # multiple lines of chords
            if chords and is_chord_line(next_line):
                self.lines.append([Chordline(line)])
                n += 1

            elif chords and not is_chord_line(next_line):
                # combine already returns a list, no need for square braces
                self.lines.append(combine(line, next_line))
                n += 2

            else: # line of lyrics
                self.lines.append([Text(line)])
                n += 1

    def __str__(self):
        formatted_lines = []
        for line in self.lines:
            print(line, "\n")
            if type(line) is Chordline or type(line) is str:
                formatted_lines.append(str(line))
                continue

            line.append(r"\\")
            formatted_lines.append(''.join([str(item) for item in line]))
        formatted_text = '\n'.join(formatted_lines)
        # drop last latex newline \\ and encapsulate stanza in its
        # type
        #return "\\{}{{\n{}\n}}\n".format(self.type, formatted_text[:-2])
        return "\\{}{{{}}}\n".format(self.type, formatted_text)


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


        

class Song(object):
    """Base song data structure in Praisetex"""
    def __init__(self, filename):
        self.attributes = {}
        self.attributes["fullpath"] = filename

        # initial attributes for song, may be written over later
        # if specified within song file
        self.attributes["title"] = os.path.basename(filename)
        self.attributes["by"] = ""
        self.attributes["comment"] = ""

        # read in song and parse the text
        with open(filename, 'r') as f:
            self.raw_text = f.read()

        self._parse()
    

    def _parse(self):
        """Parse song text and find its attributes"""
        # break up raw text into lines
        text = self.raw_text.split('\n')
        self.lines = text

        # remove empty or blank lines
        text = [line for line in text if line != '' and not line.isspace()]

        line_numbers = find_commands(text)
        line_numbers.reverse() # it's easier to search backwards through file for commands
        
        songfile_order = [] # keep order for chords

        prev = len(text)
        for num in line_numbers:
            lines = text[num:prev]
            #print(lines)
            if len(lines) == 1: # found a one line command
                pair = KeyValuePair(lines[0])
                self.attributes[pair.command] = pair.value
            
            elif len(lines) > 1: # found a multiline command
                s = Stanza(lines)
                if not s.command in self.attributes:
                    self.attributes[s.command] = s
                    songfile_order.append(s.command)
                else:
                    raise KeyError("Duplicate command in song file: {}".format(s.command))

            else:
                raise ValueError("Empty line: {}".format(num))
            prev = num

        # save stanza ordering for chords sheet
        self.attributes["chords_order"] = songfile_order

        # handle stanza ordering for slides
        songfile_order.reverse()
        if "order" in self.attributes: # song order exists
            order = self.attributes["order"]
            order = order.split(',')
            neworder = [word.strip() for word in order]
            self.attributes["slides_order"] = neworder

        else: # no order in song file, use same order for slides and chords
            self.attributes["slides_order"] = songfile_order

        
            

    def genLatex(self):
        formatted_text = []
        
        # format standard song file header info
        title = "\\songtitle{{{}}}".format(self.attributes['title'])
        formatted_text.append(title)

        by = "\\by{{{}}}".format(self.attributes['by'])
        formatted_text.append(by)

        comment = "\\comment{{{}}}".format(self.attributes['comment'])
        formatted_text.append(comment)

        # format stanzas
        for stanza in self.attributes['order']:
            formatted_text.append(str(self.attributes[stanza]))

        return '\n'.join(formatted_text)
        

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
    s = Song('testsong')
    c = s.attributes['chorus']
