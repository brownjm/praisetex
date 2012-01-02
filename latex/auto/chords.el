(TeX-add-style-hook "chords"
 (lambda ()
    (TeX-add-symbols
     '("chordline" 1)
     '("chordleft" 1)
     '("chord" 1)
     '("bridge" 1)
     '("chorus" 1)
     '("prechorus" 1)
     '("comment" 1)
     '("by" 1)
     "tochorus"
     "toprechorus"
     "framebreak")
    (TeX-run-style-hooks
     "color"
     "multicol"
     "geometry"
     "latex2e"
     "art11"
     "article"
     "11pt"
     "twoside"
     "songs/YourLoveIsExtravagant")))

