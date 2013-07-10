"""Praisetex module that handles latex generation"""

import song

commandList = ["title", "by", "comment"]
stanzaList = ["verse", "chorus", "prechorus", "bridge", "intro", "outro"]


def latex_command(command, arg):
    return "\{}{{{}}}".format(command, arg)

def chord_to_latex(chord):
    chord = chord.text.replace('#', '\#') # latex requires backslash
    return latex_command("chord", chord)

def chordline_to_latex(chordline):
    return latex_command("chordline", chordline.text)

def text_to_latex(text):
    text = text.text.replace('   ', latex_command('hspace', '3mm'))
    text = text.replace('&', '\&') # latex requires backslash
    return text

def paren_to_latex(paren):
    return latex_command("emph", "({})".format(paren.text))


if __name__ == '__main__':
    print(latex_command("emph", "hello"))
