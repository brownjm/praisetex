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

def stanza_to_latex(stanza):
    """Returns latex command for the song.Stanza class"""
    pass

if __name__ == '__main__':
    s = song.Song('testsong')
