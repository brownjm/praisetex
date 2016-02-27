praisetex
=========

Description
-----------

A program for generating chordsheets and slides for praise
music. Songs are plain text files that are converted using LaTeX into
nicely typeset chordsheets for musicians and/or slides for the
audience.

Installation
------------

In order to run praisetex, you will need
*  Python 2.7 or 3.x, including Tkinter
*  LaTeX and the Beamer class

Any LaTeX distribution that provides 'pdflatex' and contains the
Beamer class for making slides should work, though some distributions
make it easier to get started. For Windows users MikTex is recommended
as it will automatically install missing LaTeX packages when praisetex
is first run. On Linux, you should install the texlive distribution
that is from your package manager. For Mac, I believe it is best to
use MacTex.

Usage
-----
The easiest way to produce chordsheets or slides is with the GUI. Simply run
>  python praisetex.py

All of the features in the GUI are also available via command line too. Run
>  python praisetex.py -h

to see what features are available.

Songs are stored as plain text files in the 'songs' directory. To
compile a song highlight it or many in the list of available songs,
use the button marked 'Add' to move to the songs to be compiled
list. Then click slides to generate slides and chords to generate
chordsheets.

License
-------
praisetex - a simple set of programs for creating praise music material, 
such as guitar chordsheets and presentation slides

Copyright &copy; 2016 Jeffrey M Brown
brown.jeffreym@gmail.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.