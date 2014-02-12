"""Handles conversions to and from plain text song file format"""
import re

# valid letters for chords
valid_chords = "ABCDEFGb#minajsugd123456789"
not_chords = "HJKLOPQRTVWXYZ\n"

# regex to find location of chords such as A or D/F#
chord_loc_regex = re.compile("[A-G][1-9#bMminAajSsugDd]*[/]*[A-G]*[1-9#bMminAajSsugDd]*")

# regex to break apart chords into their attributes
root = "(^[A-G])"
accidental = "(#|b)*"
quality = "([[Mm]aj|M|[Mm]in|m|sus|aug|dim)*"
interval = r"(\d)*"
chord = root + accidental + quality + interval
chord_attr_regex = re.compile(chord)

def to_text(ast):
    """Convert ast to plain text song format"""
    pass

    
def to_ast(text):
    """Convert plain text song format to ast"""
    lines = text.split('\n')
    song = _parse_structure(lines)
    song['order'] = _handle_order(song['order'])
    song['stanzas'] = [_handle_stanza(s) for s in song['stanzas']]
    return song


def _parse_structure(lines):
    """Return structured dictionary of plain text song file"""
    def is_empty(line):
        return line.isspace() or len(line) == 0

    def is_command(line):
        return ':' in line

    lines.reverse()
    stack = []
    song = {}
    song['stanzas'] = []
    for line in lines:
        if is_empty(line):
            continue
        if is_command(line):
            first, second = line.split(':')
            first = first.strip()
            second = second.strip()
            if len(stack) == 0: # not stanza, but is key-value pair
                song[first] = second
            else: # stanza
                stack.append(first)
                stack.reverse()
                song['stanzas'].append(stack)
                stack = []
        else:
            stack.append(line)
    song['stanzas'].reverse()
    return song


def _handle_order(order_list):
    lst = order_list.split(',')
    new_list = []
    for item in lst:
        items = item.split()
        first = items[0]
        if len(items) == 1:
            second = None
        else:
            second = int(items[1])
        new_list.append({first:second})
    return new_list


def _handle_stanza(stanza):
    """Restructure stanzas into ast format"""
    new_stanza = {}
    command = stanza[0].split()
    if len(command) == 1:
        new_stanza["type"] = command[0]
        new_stanza["number"] = None
    else:
        typ, num = command
        new_stanza["type"] = typ
        new_stanza["number"] = num
    lines = _handle_lines(stanza[1:])
    new_stanza["lines"] = lines
    return new_stanza


def _handle_lines(lines):
    """Find and merge chordlines and text"""
    chord_regex = re.compile("[A-G][1-9#bminajsugd]*[/]*[A-G]*[1-9#bminajsugd]*")
    new_lines = []
    length = len(lines)
    stack = [] # temporarily hold chord lines
    for line in lines:
        if _is_chord_line(line):
            if len(stack) != 0:
                chords = _handle_chords(stack.pop())
                new_lines.append({"chords": chords, "text": None})
            stack.append(line)
        else: # line is lyrics
            if len(stack) != 0:
                chords = _handle_chords(stack.pop())
                new_lines.append({"chords": chords, "text": line})

            else:
                new_lines.append({"chords": None, "text": line})

    # handle chordline at end of stanza
    if len(stack) != 0:
        new_lines.append({"chords": _handle_chords(stack.pop())})

    return new_lines



def _handle_chords(chords):
    """Find all chords and build list of {base, modifier, position, length}"""
    matches = chord_loc_regex.finditer(chords)
    
    # tuples of (location, chord text)
    chords = list(zip([m.start() for m in matches], chords.split()))
    new_chords = []
    for c in chords:
        chord = {}
        chord["loc"], chord["text"] = c
        chord["length"] = len(c[1])
        chord.update(_split_chord(c[1]))
        new_chords.append(chord)
    return new_chords

def _split_chord(chord):
    d = {}
    chords = chord.split("/")
    match = chord_attr_regex.search(chords[0])
    d["root"], d["accidental"], d["quality"], d["interval"] = match.groups()
    d["base"] = None

    # handle base note it any exists
    if len(chords) > 1:
        b = {}
        match = chord_attr_regex.search(chords[1])
        b["root"], b["accidental"], b["quality"], b["interval"] = match.groups()
        d["base"] = b

    return d

def _is_chord_line(line):
    """Checks if the line contains chords"""
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


    if contains_only(line, valid_chords) and not contains_any(line, not_chords):
        return True
    else:
        return False


if __name__ == '__main__':
    with open('10000Reasons.txt', 'r') as f:
        text = f.read()

    ast = to_ast(text)
    
    
    stanzas = ast['stanzas']
