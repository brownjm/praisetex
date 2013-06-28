"""New song class to work with a plain text song file format"""

import os

commandList = ["title", "by", "comment"]
stanzaList = ["verse", "chorus", "prechorus", "bridge", "intro", "outro"]

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
        self.lines = text[1:]
        

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
        """Parse song text and convert it into praisetex's latex format"""
        # break up raw text into lines
        text = self.raw_text.split('\n')
        self.lines = text

        # remove empty or blank lines
        text = [line for line in text if line != '' and not line.isspace()]

        line_numbers = find_commands(text)
        line_numbers.reverse() # it's easier to search backwards through file for commands
        
        backup_order = [] # in case an order isn't specified in the file

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
                    backup_order.append(s.command)
                else:
                    raise KeyError("Duplicate command in song file: {}".format(s.command))

            else:
                raise ValueError("Empty line: {}".format(num))
            prev = num

        # handle stanza ordering
        if not "order" in self.attributes: # use backup ordering of stanzas
            backup_order.reverse()
            self.attributes["order"] = backup_order

        else: # order specified in file
            order = self.attributes["order"]
            order = order.split(',')
            neworder = [word.strip() for word in order]
            self.attributes["order"] = neworder
            


def find_commands(text):
    """Returns a list of line numbers which contain a colon, representing a command"""
    line_numbers = []
    num = 0
    for line in text:
        if ":" in line:
            line_numbers.append(num)
        num += 1
            
    return line_numbers



if __name__ == '__main__':
    s = Song('testsong')
