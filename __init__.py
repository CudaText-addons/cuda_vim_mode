from cudatext import *
import cudatext_cmd as cc
import cudatext_keys as ck
from .word_proc import *

def msg(s):
    msg_status('[Vim] '+s)


class Command:
    active = False
    insert = False
    replace_char = False
    prefix_g = False
    number = ''


    def toggle_active(self):
        self.insert = False
        self.active = not self.active
        if self.active:
            msg('plugin activated')
        else:
            msg('plugin deactivated')


    def on_key(self, ed_self, key, state):
        if not self.active: return

        if key==ck.VK_ESCAPE:
            if self.insert:
                self.insert = False
                ed.set_prop(PROP_INSERT, True)
                msg('command mode')
                return False
            else:
                return

        if key in [ck.VK_LEFT, ck.VK_RIGHT, ck.VK_UP, ck.VK_DOWN,
                    ck.VK_PAGEUP, ck.VK_PAGEDOWN]:
            msg('arrow key')
            return

        if self.insert:
            msg('insertion mode')
            return

        if state in ['', 's']:
            if self.replace_char:
                return

            if ord('0')<=key<=ord('9'):
                self.number += chr(key)
                msg('number: '+self.number)
                return False

            if key==ord('G') and state=='':
                if not self.prefix_g:
                    self.prefix_g = True
                    msg('go to?')
                else:
                    self.prefix_g = False
                    ed.cmd(cc.cCommand_GotoTextBegin)
                    msg('go to text begin')
                return False
            else:
                self.prefix_g = False

            if key==ord('G') and state=='s':
                if self.number=='':
                    ed.cmd(cc.cCommand_GotoTextEnd)
                    msg('go to text end')
                else:
                    try:
                        index = int(self.number)-1
                    except:
                        index = -1
                    if 0<=index<ed.get_line_count():
                        x0, y0, x1, y1 = ed.get_carets()[0]
                        ed.set_caret(x0, index)
                        ed.cmd(cc.cCommand_ScrollToCaretTop)
                        msg('go to line '+self.number)
                    else:
                        msg('incorrect line number: '+self.number)
                    self.number = ''
                return False

            if key==ord('H') and state=='':
                ed.cmd(cc.cCommand_KeyLeft)
                msg('left')
                return False

            if key==ord('J') and state=='':
                ed.cmd(cc.cCommand_KeyDown)
                msg('down')
                return False

            if key==ord('K') and state=='':
                ed.cmd(cc.cCommand_KeyUp)
                msg('up')
                return False

            if key==ord('L') and state=='':
                ed.cmd(cc.cCommand_KeyRight)
                msg('right')
                return False

            if key==ord('B') and state=='':
                ed.cmd(cc.cCommand_GotoWordPrev)
                msg('go to prev word')
                return False

            if key==ord('W') and state=='':
                ed.cmd(cc.cCommand_GotoWordNext)
                msg('go to next word')
                return False

            if key==ord('E') and state=='':
                goto_word_end()
                msg('go to word end')
                return False

            if key==ord('A') and state=='':
                ed.cmd(cc.cCommand_KeyRight)
                self.insert = True
                msg('insertion mode, after current char')
                return False

            if key==ord('I') and state=='':
                self.insert = True
                msg('insertion mode, at current char')
                return False

            if key==ord('X') and state=='':
                ed.cmd(cc.cCommand_KeyDelete)
                msg('delete char')
                return False

            if key==ord('X') and state=='s':
                ed.cmd(cc.cCommand_KeyBackspace)
                msg('delete char left')
                return False

            if key==ord('R') and state=='':
                self.replace_char = True
                msg('replace char to')
                return False

            if key==ord('R') and state=='s':
                self.insert = True
                ed.set_prop(PROP_INSERT, False)
                msg('replace mode for current line')
                return False

            if key==ord('O') and state=='s':
                ed.cmd(cc.cCommand_TextInsertEmptyAbove)
                self.insert = True
                msg('insert line above, insertion mode')
                return False

            if key==ord('O') and state=='':
                ed.cmd(cc.cCommand_TextInsertEmptyBelow)
                self.insert = True
                msg('insert line below, insertion mode')
                return False

            if key==ord('D') and state=='s':
                ed.cmd(cc.cCommand_TextDeleteToLineEnd)
                msg('delete to end of line')
                return False


    def on_key_up(self, ed_self, key, state):
        if not self.active: return


    def on_insert(self, ed_self, text):
        if not self.active:
            return

        if self.insert:
            return

        if self.replace_char:
            self.replace_char = False

            x0, y0, x1, y1 = ed.get_carets()[0]
            ed.replace(x0, y0, x0+len(text), y0, text)

            msg('replace char to: '+text)
            return False

        if text=='|':
            x0, y0, x1, y1 = ed.get_carets()[0]

            if self.number=='':
                index = 0
            else:
                try:
                    index = int(self.number)-1
                except:
                    index = -1
                self.number = ''

                nlen = len(ed.get_text_line(y0))
                if not 0<=index<=nlen:
                    msg('incorrect column: '+str(index+1))
                    return False

            ed.set_caret(index, y0)
            msg('go to column '+str(index+1))
            return False


        if not self.replace_char:
            msg('key not handled')
            return False

