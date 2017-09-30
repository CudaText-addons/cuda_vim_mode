plugin for CudaText.
if activated (via command in Plugins), it activates Vim key bindings, initially in Vim command mode.
not all Vim keys are supported.

a) Vim insertion mode - all keys work like usual in CudaText, only Esc goes to command mode
b) Vim replace mide- like insertion mode, but "insert/overwrite mode" is "overwrite"
c) Vim command mode has supported keys:

  hjkl - caret movement
  w - go to next word (jumps not exactly like Vim, but like CudaText command "go to next word")
  b - go to previous word (same note)
  e - go to end of word (or next word)
  a - enter insertion mode, after moving caret right
  i - enter insertion mode, at current pos
  x - delete char right (like Delete key)
  X - delete char left (like Backspace key)
  r - replace current char with next typed char, return to command mode
  R - enter replace mode


author: Alexey (CudaText)
license: MIT
