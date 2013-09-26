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

# removes empty lists
def remove_empty_list(lst):
    """Remove empty list from song"""
    for index, element in enumerate(lst):
        if isinstance(element, list):
            if len(element) == 0:
                lst.pop(index)
            else:
                remove_empty_list(element)
        else:
            pass


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

def cleanup_capo_command(index, element, parent):
    if isinstance(element, Command) and element.text == 'capo' and len(parent) == 2:
        # make sure capo argument is classified as Text and not Chordline, etc
        if isinstance(parent[1], str):
            parent[1] = s.Text(parent[1].strip())
        else:
            parent[1] = s.Text(parent[1].text.strip())

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
        combined.append('\\\\\n') # keep lines separate
        combined.reverse()
        for item in combined:
            parent.insert(index, item)



class Command(object):
    """Represents a command within a song file"""
    def __init__(self, text):
        self.text = text.strip()
        textlist = self.text.split()
        self.command = textlist[0].lower()

        if len(textlist) == 1:
            self.command_arg = None
        else:
            self.command_arg = textlist[1]


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

# handle chords order command
def handle_chords_order(index, element, parent):
    if isinstance(element, Command) and element.text == 'order':
        args = []
        for i in range(len(parent[1:])):
            args.append(parent.pop(1).text)
        parent.append(', '.join(args))


def handle_slides_order(song):
    stanzas = ["verse", "chorus", "prechorus", "bridge", "intro", "outro", "tag", "break", "order"]
    stanzadict = {}
    newsong = []

    def collect(index, element, parent):
        if isinstance(element, Command):
            if element.command in stanzas:
                stanzadict[element.text] = parent
            else:
                newsong.append(parent)

    apply_pass(song, collect)

    if "order" in stanzadict:
        order = stanzadict["order"]
    else:
        return song

    order = [item.text for item in order[1:]]

    for stanza in order:
        newsong.append(stanzadict[stanza])

    return newsong


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
        chords = element.text.replace('#', '\#') # latex requires backslash
        chords = chords.replace('b', '$\\flat$') # change to latex's flat symbol
        parent[index] = latex_command("chordline", chords)


parenthesis_regex = re.compile("\((.+)\)")

def parenthesis_to_latex(index, element, parent):
    """Handle emphasized text surrounded by parentheses"""
    if isinstance(element, s.Text):
        match = re.search(parenthesis_regex, element.text)
        if match is not None:
            text = match.groups()[0]
            parent[index] = latex_command("emph", "({})".format(text))

def remove_parenthesis(index, element, parent):
    """Remove any words surrounded by parenthesis"""
    if isinstance(element, s.Text):
        match = re.search(parenthesis_regex, element.text)
        if match is not None:
            parent.pop(index)


def spacing_to_latex(index, element, parent):
    """Produce latex code to handle explicit spacing between words"""
    if isinstance(element, s.Text):
        parent[index] = element.text.replace("   ", latex_command("hspace", "3mm"))

def ampersand_to_latex(index, element, parent):
    """Replace ampersand symbol with latex one"""
    if isinstance(element, s.Text):
        parent[index] = element.text.replace('&', '\&')

# maps song file commands to their equivalent latex command
command_map = {"title": "songtitle",
               "by": "by",
               "comment": "comment",
               "capo": "capo",
               "scripture": "scripture",
               "order": "order",
               "verse": "verse",
               "chorus": "chorus",
               "prechorus": "prechorus",
               "bridge": "bridge",
               "intro": "intro",
               "outro": "outro",
               "tag": "tagline",
               "break": "songbreak",
               "format": "songformat"}

def check_command_validity(index, element, parent):
    """Check that commands are valid song file ones"""
    if isinstance(element, Command):
        if not element.command in command_map.keys():
            raise RuntimeError("Command not valid: {}".format(element.command))

def command_to_latex(index, element, parent):
    """Produce latex code for the commands and their arguments"""
    if isinstance(element, Command):
        command = command_map[element.command]
        if element.command_arg != None:
            command = command + "[~" + element.command_arg + "]"

        #print(command)

        args = parent[1:]
        for i in range(len(args)):
            parent.pop(-1)
        parent[index] = latex_command(command, ''.join(args))

def slides_command_to_latex(index, element, parent):
    """Produce latex code for the slides commands and their arguments"""
    if isinstance(element, Command):
        command = command_map[element.command]
        if element.command_arg != None:
            command = command + "[~" + element.command_arg + "]"

        #print(command)

        args = parent[1:]
        for i in range(len(args)):
            parent.pop(-1)
        parent[index] = latex_command(command, '\\\\\n'.join(args))



def remove_chords(index, element, parent):
    """Remove chords from song"""
    if isinstance(element, s.Chordline) or isinstance(element, s.Chord):
        parent.pop(index)

def remove_capo(index, element, parent):
    """Remove capo command from song"""
    if isinstance(element, Command) and element.text == 'capo':
        #parent.clear() # python 3 only
        del parent[:]

def remove_order(index, element, parent):
    """Removes the order command"""
    if isinstance(element, Command) and element.text == 'order':
        #for i in range(len(parent)):
        #    parent.pop(-1)
        del parent[:] # clear contents of parent list
        #parent.clear() # python 3 only

def remove_empty_latex_commands(index, element, parent):
    """Removes empty latex commands"""
    if isinstance(element, str):
        if "{}" in element:
            parent.pop(index)

def elements_to_string(songlist):
    """Combine all elements into a string separated by newlines"""
    songlist.append('\n')
    songlist = [element[0] for element in songlist]
    return '\n'.join(songlist)



def compile_chords(filename):
    """Converts a song file into latex code for a chordsheet"""
    with open(filename, 'r') as f:
        lines = f.read().split('\n')
    song = parse_structure(lines)

    # clean up and find commands
    apply_pass(song, split_by_colon)
    apply_pass(song, remove_empty_lines)
    apply_pass(song, identify_commands)
    apply_pass(song, check_command_validity)

    # clean up command arguments
    apply_pass(song, cleanup_title_command)
    apply_pass(song, cleanup_by_command)
    apply_pass(song, cleanup_title_command)
    apply_pass(song, cleanup_order_command)
    apply_pass(song, cleanup_comment_command)
    apply_pass(song, cleanup_capo_command)

    # process chords and lyrics
    apply_pass(song, identify_chordlines)
    apply_pass(song, identify_text)
    apply_pass(song, merge_chords_lyrics)
    apply_pass(song, identify_text)


    # handle order
    apply_pass(song, handle_chords_order)
    remove_empty_list(song)

    # latex generation
    apply_pass(song, chord_to_latex)
    apply_pass(song, chordline_to_latex)
    apply_pass(song, parenthesis_to_latex)
    apply_pass(song, spacing_to_latex)
    apply_pass(song, ampersand_to_latex)
    apply_pass(song, remove_empty_latex_commands)
    apply_pass(song, command_to_latex)


    # final clean up of empty lists
    remove_empty_list(song)

    # # combine all elements into a single string
    song = elements_to_string(song)

    return song


def compile_slides(filename):
    """Converts a song file into latex code for presentation slides"""
    with open(filename, 'r') as f:
        lines = f.read().split('\n')
    song = parse_structure(lines)

    # clean up and find commands
    apply_pass(song, split_by_colon)
    apply_pass(song, remove_empty_lines)
    apply_pass(song, identify_commands)
    apply_pass(song, check_command_validity)

    # clean up command arguments
    apply_pass(song, cleanup_title_command)
    apply_pass(song, cleanup_by_command)
    apply_pass(song, cleanup_title_command)
    apply_pass(song, cleanup_order_command)
    apply_pass(song, cleanup_comment_command)
    apply_pass(song, cleanup_capo_command)

    # process chords and lyrics
    apply_pass(song, identify_chordlines)
    apply_pass(song, remove_chords)
    apply_pass(song, remove_chords)
    apply_pass(song, remove_capo)

    apply_pass(song, identify_text)
    apply_pass(song, remove_parenthesis)
    remove_empty_list(song)
    #apply_pass(song, print_item)


    # # handle order
    song = handle_slides_order(song)
    #apply_pass(song, print_item)


    # # latex generation
    #apply_pass(song, chord_to_latex)
    #apply_pass(song, chordline_to_latex)
    # apply_pass(song, parenthesis_to_latex)
    #apply_pass(song, spacing_to_latex)
    apply_pass(song, ampersand_to_latex)
    apply_pass(song, slides_command_to_latex)

    # # final clean up of empty lists
    remove_empty_list(song)
    apply_pass(song, remove_empty_latex_commands)
    remove_empty_list(song)

    # # combine all elements into a single string
    song = elements_to_string(song)

    return song

if __name__ == '__main__':
    songname = 'songs/OLoveThatWillNotLetMeGo.txt'
    song = compile_chords(songname)
    #song = compile_slides(songname)
