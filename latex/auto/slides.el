(TeX-add-style-hook "slides"
 (lambda ()
    (TeX-add-symbols
     '("comment" 1)
     '("chordline" 1)
     '("chordleft" 1)
     '("chord" 1)
     '("bridge" 1)
     '("prechorus" 1)
     '("chorus" 1)
     '("by" 1)
     "tochorus"
     "toprechorus")
    (TeX-run-style-hooks
     "latex2e"
     "beamer10"
     "beamer"
     "20pt"
     "songs/YouAreMyKing")))

