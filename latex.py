"""Praisetex module that handles latex generation"""

import song

commandList = ["title", "by", "comment"]
stanzaList = ["verse", "chorus", "prechorus", "bridge", "intro", "outro"]


def latex_command(command, arg):
    """Returns a latex command with a single argument"""
    return "\{}{{{}}}".format(command, arg)

def chord_to_latex(chord):
    """Returns latex command for the song.Chord class"""
    chord = chord.text.replace('#', '\#') # latex requires backslash
    return latex_command("chord", chord)

def chordline_to_latex(chordline):
    """Returns latex command for the song.Chordline class"""
    return latex_command("chordline", chordline.text)

def text_to_latex(text):
    """Returns latex command for the song.Text class"""
    text = text.text.replace('   ', latex_command('hspace', '3mm'))
    text = text.replace('&', '\&') # latex requires backslash
    return text

def paren_to_latex(paren):
    """Returns latex command for the song.Parentheses class"""
    return latex_command("emph", "({})".format(paren.text))



def to_latex(song_element):
    """Function that calls appropriate latex conversion function for given song element"""
    if isinstance(song_element, song.Chord):
        return chord_to_latex(song_element)
    elif isinstance(song_element, song.Text):
        return text_to_latex(song_element)
    elif isinstance(song_element, song.Chordline):
        return chordline_to_latex(song_element)
    elif isinstance(song_element, song.Parentheses):
        return paren_to_latex(song_element)
    else:
        raise ValueError("Unknown song element: {}".format(type(song_element)))


def stanza_to_latex(stanza):
    """Returns latex code for the song.Stanza class"""
    formatted_lines = []
    for line in stanza.lines:
        formatted_lines.append(''.join([to_latex(element) for element in line]))
    text = '\\\\\n'.join(formatted_lines) # add latex newline \\ and ascii newline
    return latex_command(stanza.type, text)

def song_to_latex(song):
    """Returns latex code for the song.Song class"""
    pass
    
def write(text):
    with open('test', 'w') as f:
        f.write(text)

if __name__ == '__main__':
    s = song.Song('testsong')
    c = s.attributes['chorus']
