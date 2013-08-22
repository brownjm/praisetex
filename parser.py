"""Parser for praisetex song files"""

import re
import song as s

# applies a single pass of the nano pass compilation process
def replace_element(song, function):
    """Apply a function onto each element of a list of lists"""
    for index, element in enumerate(song):
        if isinstance(element, list): # if it is a sublist
            replace_element(element, function)
        else: # an atomic element
            song[index] = function(element) # replace its value

# applies a single pass of the nano pass compilation process
def apply_pass(lst, function, parent=None):
    """Apply a function onto each element of a list of lists"""
    for index, element in enumerate(lst):
        if not isinstance(element, list):
            # apply function to atomic element
            function(index, element, lst)
        else: # another list
            apply_pass(element, function, parent=lst)


# # applies a single pass of the nano pass compilation process
# def apply_pass(lst, function, parent=None):
#     """Apply a function onto each element of a list of lists"""
#     for index, element in enumerate(lst):
#         if isinstance(element, list): # if it is a sublist
#             apply_pass(element, function, parent=lst)
#         else: # an atomic element
#             function(index, element, lst)

def remove_empty_lines(index, element, parent):
    if not isinstance(element, str):
        return
    if element.isspace() or len(element) == 0:
        parent.pop(index)

def split_by_colon(index, element, parent):
    if not isinstance(element, str):
        return
    if ':' in element:
        parent.pop(index)
        first, second = element.split(':')
        parent.insert(index, second)
        parent.insert(index, first)

def trim_whitespace(index, element, parent):
    if isinstance(element, str):
        parent[index] = element.strip()

def cleanup_order_command(index, element, parent):
    if isinstance(element, Command) and element.text == 'order' and len(parent) == 2:
        order_list = parent[1].split(',')
        parent.pop(1)
        order_list.reverse()
        for item in order_list:
            parent.insert(1, item.strip())

def cleanup_title_command(index, element, parent):
    if isinstance(element, Command) and element.text == 'title' and len(parent) == 2:
        parent[1] = parent[1].strip()

def cleanup_by_command(index, element, parent):
    if isinstance(element, Command) and element.text == 'by' and len(parent) == 2:
        parent[1] = parent[1].strip()

def cleanup_comment_command(index, element, parent):
    if isinstance(element, Command) and element.text == 'comment' and len(parent) == 2:
        parent[1] = parent[1].strip()
        
def merge_chords_lyrics(index, element, parent):
    if not isinstance(element, s.Chordline):
        return
        # handle dangling chordline at end of stanza
    if index == len(parent)-1: # if last element of parent
        return
    elif isinstance(parent[index+1], s.Chordline):
        # next line is also a chordline
        return
    else:
        # next line is lyrics
        chords = parent.pop(index)
        lyrics = parent.pop(index)
        combined = s.combine(chords.text, lyrics.text)
        combined.append('\n') # keep lines separate
        combined.reverse()
        for item in combined:
            parent.insert(index, item)
            
class Command(object):
    """Represents a command within a song file"""
    def __init__(self, text):
        self.text = text.strip()

def identify_commands(index, element, parent):
    if isinstance(element, str) and index == 0:
        parent.pop(index)
        parent.insert(index, Command(element))

def identify_chordlines(index, element, parent):
    if isinstance(element, str):
        if s.is_chord_line(element):
            parent.pop(index)
            parent.insert(index, s.Chordline(element))

def identify_text(index, element, parent):
    if isinstance(element, str):
        if not s.is_chord_line(element):
            parent.pop(index)
            parent.insert(index, s.Text(element))

def parse_structure(lines):
    """Break up song text into list of lists"""
    lines.reverse() # easier to group stanzas in reverse
    stack = []
    songlist = []
    for item in lines:
        if ':' in item:
            stack.append(item)
            stack.reverse()
            songlist.append(stack)
            stack = []
        else:
            stack.append(item)
    songlist.reverse()
    lines.reverse()
    return songlist

def print_item(index, element, parent):
    if isinstance(element, str):
        print(element)
    else:
        print(element.text)

# latex generation
def latex_command(command, arg):
    """Returns a latex command with a single argument"""
    return "\{}{{{}}}".format(command, arg)

def chord_to_latex(index, element, parent):
    """Returns latex command for Chord class"""
    if isinstance(element, s.Chord):
        chord = element.text.replace('#', '\#') # latex requires backslash
        chord = chord.replace('b', '$\\flat$') # change to latex's flat symbol
        parent[index] = latex_command("chord", chord)

def chordline_to_latex(index, element, parent):
    """Returns latex command for the song.Chordline class"""
    if isinstance(element, s.Chordline):
        parent[index] = latex_command("chordline", element.text)


paren_regex = re.compile("\((.+)\)")

def paren_to_latex(index, element, parent):
    """Handle emphasized text surrounded by parentheses"""
    if isinstance(element, s.Text):
        match = re.search(paren_regex, element.text)
        if match is not None:
            text = match.groups()[0]
            parent[index] = latex_command("emph", "({})".format(text))

def spacing_to_latex(index, element, parent):
    """Produce latex code to handle explicit spacing between words"""
    if isinstance(element, s.Text):
        parent[index] = element.text.replace("   ", latex_command("hspace", "3mm"))

def ampersand_to_latex(index, element, parent):
    """Replace ampersand symbol with latex one"""
    if isinstance(element, s.Text):
        parent[index] = element.text.replace('&', '\&')


commandList = ["title", "by", "comment", "verse", "chorus", "prechorus", "bridge", "intro", "outro"]

def command_to_latex(index, element, parent):
    """Produce latex code for the commands and their arguments"""
    if isinstance(element, Command):
        command = element.text
        args = parent[1:]
        for i in range(len(args)):
            parent.pop(-1)
        parent[index] = latex_command(command, ''.join(args))

def remove_chords(index, element, parent):
    """Remove chords from song"""
    if isinstance(element, s.Chordline) or isinstance(element, s.Chord):
        parent.pop(index)

if __name__ == '__main__':
    with open('test', 'r') as f:
        lines = f.read().split('\n')

    song = parse_structure(lines)

    # clean up and find commands
    apply_pass(song, split_by_colon)
    apply_pass(song, remove_empty_lines)
    apply_pass(song, identify_commands)

    # clean up command arguments
    apply_pass(song, cleanup_title_command)
    apply_pass(song, cleanup_by_command)
    apply_pass(song, cleanup_title_command)
    apply_pass(song, cleanup_order_command)
    apply_pass(song, cleanup_comment_command)

    # process chords and lyrics
    apply_pass(song, identify_chordlines)
    apply_pass(song, identify_text)
    #apply_pass(song, remove_chords)
    apply_pass(song, merge_chords_lyrics)
    # identify newlines produced by merge_chords_lyrics
    apply_pass(song, identify_text)
    #apply_pass(song, print_item)

    # # latex generation
    apply_pass(song, chord_to_latex)
    apply_pass(song, chordline_to_latex)
    apply_pass(song, paren_to_latex)
    apply_pass(song, spacing_to_latex)
    apply_pass(song, ampersand_to_latex)
    apply_pass(song, command_to_latex)

    
