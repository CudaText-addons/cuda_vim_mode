plugin for CudaText.
command in Plugins menu activates Vim key bindings, initially in Vim command mode. Vim mode is activated in all editor tabs at once. indication of Vim mode is full-block-framed caret. 

a) Vim insertion mode - all keys work like usual in CudaText, only Esc goes to command mode
b) Vim replace mode - like insertion mode, but "insert/overwrite mode" is "overwrite"
c) Vim visual mode - all movement keys (arrows/home/end/pageup/pagedown) make selection w/o Shift
d) Vim command mode supported keys:

  h, j, k, l - caret movement

  w - go to next word (jumps not exactly like Vim, but like CudaText command "go to next word")
  b - go to previous word (same note)
  e - go to end of word (or next word)

  a - enter insertion mode, after moving caret right
  i - enter insertion mode, at current pos
  R - enter replace mode
  r - replace current char with next typed char, return to command mode

  o - creates empty line below, goes into insertion mode on new line
  O - creates empty line above, goes into insertion mode on new line

  gg - go to text begin
  G - go to line number (if number entered before), or go to text end (if none)
  | - go to column number (if number entered before, else column 1)

  x - delete char right (like Delete key)
  X - delete char left (like Backspace key)

  D - delete to end of line
  dd - delete current line
  db - delete to word begin
  dw, de - delete to word end (currently commands work the same)
  dL - delete to text end
  d/ - delete until text position (text is asked in dialog)

  c - change - like "d" commands (cd, cb, cw, ce...) but also goes to insertion mode 
  
  v - enter visual mode
  V - enter visual mode, but select entire lines
  

author: Alexey (CudaText)
suggestions by @mangobait
license: MIT
