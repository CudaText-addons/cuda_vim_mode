plugin for CudaText.
command in Plugins menu activates Vim key bindings, initially in Vim command mode. Vim mode is activated in all editor tabs at once. 

indication of modes:
- Vim command mode: full-block-frame caret
- Vim visual mode: half-block caret
- Vim insertion mode: no indication, usual caret
 

a) Vim insertion mode - all keys work like usual in CudaText, only Esc goes to command mode
b) Vim replace mode - like insertion mode, but "insert/overwrite mode" is "overwrite"
c) Vim visual mode - all movement keys (arrows/home/end/pageup/pagedown) make selection w/o Shift
d) Vim command mode supported keys:

  h, j, k, l - move caret (4 arrows)

  w - go to next word (jumps not exactly like Vim, but like CudaText command "go to next word")
  W - currently the same as 'w'
  b - go to previous word (same note)
  B - currently the same as 'b'
  e - go to end of word (or next word)
  E - currently the same as 'e'

  a - enter insertion mode, after moving caret right
  A - enter insertion mode, at line end
  i - enter insertion mode, at current pos
  I - enter insertion mode, at first non-space char in line
  
  r - replace current char with next typed char, return to command mode
  R - enter replace mode

  o - creates empty line below, goes into insertion mode on new line
  O - creates empty line above, goes into insertion mode on new line

  gg - go to text begin
  G - go to line number (if number entered before), or go to text end (if none)

  | - go to column number (if number entered before, else column 1)
  0 - go to line begin (column 1)
  ^ - go to first non-whitespace
  - - go to first non-whitespace, in previous line
  + - go to first non-whitespace, in next line
  $ - go to line end

  x - delete char right (like Delete key)
  X - delete char left (like Backspace key)
  
  y - yank (copy) to clipboard
  Y - yank entire line
  p - paste from clipboard, after caret
  P - paste from clipboard, before caret
  d - cut to clipboard (only if text selected, else it's prefix)

  D - delete to end of line
  dd - delete current line
  db - delete to word begin
  dw, de - delete to word end (currently commands work the same)
  dL - delete to text end
  d/ - delete until position of text, which is asked in dialog
  df - delete until position of char entered after
  dt - delete until position of char entered after, minus one char
  dF - backward version of 'df'
  dT - backward version of 'dt'

  C - change to end of line (delete to end of line, go to insertion mode)
  c - change - like "d" commands (cd, cb, cw, ce...) but also goes to insertion mode 
  
  v - enter visual mode
  V - enter visual mode, but select entire lines
  
  Space - move right
  Backspace - move left
  
  / - search forward, prompts for string in dialog
  ? - search backward
  n - repeat search in the same direction
  N - repeat search in the opposite direction
  f - find next typed character, inside line
  F - backward version of "f"
  t - like "f" but set position minus one char
  T - backward version of "t"  

  u - undo
  ~ - invert case of selection (if selection) or one char
  # - go to next occurence of current word (looping from begin)
  . - repeat last command (entered in command mode)
  
  H - go to top line on screen
  M - go to middle line on screen
  L - go to bottom line on screen

  J - join current line with the next one
  S - substitute line - delete line, go to insertion mode
    
  zz - center the caret's line on screen
  z. - center the caret's line on screen, caret on first non-blank char
  zt - scroll the screen so the caret is at the top
  zb - scroll the screen so the caret is at the bottom

  ZZ - save current file, quit
  ZQ - quit without saving current file

  Ctrl+[  - the same as Esc key (removes multi-carets and returns from insertion mode to command mode)
  Ctrl+I  - the same as Tab key
  Ctrl+M  - the same as Enter key
  Ctrl+H  - the same as Backspace key
  Ctrl+F  - the same as PageDown key
  Ctrl+B  - the same as PageUp key


author: Alexey Torgashin (CudaText)
suggestions/testing: @mangobait, @oO0XX0Oo, @acicovic, @nochiel
license: MIT
