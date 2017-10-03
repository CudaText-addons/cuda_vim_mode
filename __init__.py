from cudatext import *
import cudatext_cmd as cc
import cudatext_keys as ck
from .word_proc import *

def msg(s):
    msg_status('[Vim] '+s)


class Command:
    active = False
    insert = False
    visual = False
    visual_lines = False
    visual_start = None
    replace_char = False
    prefix_g = False
    prefix_c = False
    prefix_d = False
    number = ''
    caret_normal = 2


    def update_caret(self):
        if self.insert or not self.active:
            value = self.caret_normal
        elif self.visual:
            value = 25
        else:
            value = 26
        ed.set_prop(PROP_CARET_SHAPE, value)


    def toggle_active(self):
        self.insert = False
        self.active = not self.active
        if self.active:
            self.caret_normal = ed.get_prop(PROP_CARET_SHAPE)
            msg('plugin activated')
        else:
            msg('plugin deactivated')
        self.update_caret()


    def on_key(self, ed_self, key, state):
        if not self.active: return

        if key==ck.VK_ESCAPE:
            if self.insert:
                self.insert = False
                self.update_caret()
                ed.set_prop(PROP_INSERT, True)
                msg('command mode')
                return False
            elif self.visual:
                self.visual = False
                self.visual_lines = False
                self.visual_start = None
                self.update_caret()
                msg('command mode')
                return False
            else:
                self.prefix_d = False
                self.prefix_g = False
                msg('Esc')
                return

        if key==ck.VK_BACKSPACE:
            ed.cmd(cc.cCommand_KeyLeft)
            msg('move left')
            return False

        if key in [ck.VK_LEFT, ck.VK_RIGHT, ck.VK_UP, ck.VK_DOWN,
                   ck.VK_PAGEUP, ck.VK_PAGEDOWN,
                   ck.VK_HOME, ck.VK_END]:
            if self.visual:
                xx, yy = self.visual_start
                x0, y0, x1, y1 = ed.get_carets()[0]
                y_max = ed.get_line_count()-1

                if key==ck.VK_LEFT:
                    if x0>0:
                        x0-=1
                elif key==ck.VK_RIGHT:
                    x0+=1
                elif key==ck.VK_UP:
                    if y0>0:
                        y0-=1
                elif key==ck.VK_DOWN:
                    if y0<y_max:
                        y0+=1
                elif key==ck.VK_PAGEUP:
                    y0 = max(0, y0-ed.get_prop(PROP_VISIBLE_LINES)+1)
                elif key==ck.VK_PAGEDOWN:
                    y0 = min(y_max, y0+ed.get_prop(PROP_VISIBLE_LINES)-1)
                elif key==ck.VK_HOME:
                    x0 = 0
                elif key==ck.VK_END:
                    x0 = len(ed.get_text_line(y0))

                if self.visual_lines:
                    if y0<yy:
                        x0 = 0
                        xx = len(ed.get_text_line(yy))
                    else:
                        xx = 0
                        x0 = len(ed.get_text_line(y0))

                ed.set_caret(x0, y0, xx, yy)

                s = 'visual selection'
                if self.visual_lines:
                    s += ', by lines'
                msg(s)
                return False
            else:
                msg('movement key')
                return

        if self.insert:
            if ed.get_prop(PROP_INSERT):
                msg('insertion mode')
            else:
                msg('replace mode')
            return


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


        if text in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
            use_num = True
            if text=='0' and self.number=='':
                use_num = False
                x0, y0, x1, y1 = ed.get_carets()[0]
                ed.set_caret(0, y0)
                msg('move to line begin')
            if use_num:
                self.number += text
                msg('number: '+self.number)
            return False

        if text=='g':
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

        if text=='G':
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


        if self.prefix_c or self.prefix_d:
            if text=='d':
                ed.cmd(cc.cCommand_TextDeleteLine)
                msg('delete line')

            elif text=='w':
                ed.cmd(cc.cCommand_TextDeleteWordNext)
                msg('delete to word end')

            elif text=='e':
                ed.cmd(cc.cCommand_TextDeleteWordNext)
                msg('delete to word end')

            elif text=='b':
                ed.cmd(cc.cCommand_TextDeleteWordPrev)
                msg('delete to word begin')

            elif text=='L':
                ed.cmd(cc.cCommand_TextDeleteToTextEnd)
                msg('delete to text end')

            elif text=='/':
                s = dlg_input('Delete to text:', '')
                if s:
                    x0, y0, x1, y1 = ed.get_carets()[0]
                    res = find_text_pos(x0, y0, s)
                    if res:
                        x1, y1 = res
                        ed.delete(x0, y0, x1, y1)
                        msg('delete to text: '+s)
                    else:
                        msg('not found: '+s)
                else:
                    msg('Esc')

            if self.prefix_c:
                self.insert = True
                self.update_caret()
            self.prefix_c = False
            self.prefix_d = False
            return False


        if text=='h':
            ed.cmd(cc.cCommand_KeyLeft)
            msg('left')
            return False

        if text=='j':
            ed.cmd(cc.cCommand_KeyDown)
            msg('down')
            return False

        if text=='k':
            ed.cmd(cc.cCommand_KeyUp)
            msg('up')
            return False

        if text=='l':
            ed.cmd(cc.cCommand_KeyRight)
            msg('right')
            return False

        if text in ['b', 'B']:
            ed.cmd(cc.cCommand_GotoWordPrev)
            msg('go to prev word')
            return False

        if text in ['w', 'W']:
            ed.cmd(cc.cCommand_GotoWordNext)
            msg('go to next word')
            return False

        if text in ['e', 'E']:
            goto_word_end()
            msg('go to word end')
            return False

        if text=='a':
            ed.cmd(cc.cCommand_KeyRight)
            self.insert = True
            self.update_caret()
            msg('insertion mode, after current char')
            return False

        if text=='A':
            self.insert = True
            self.update_caret()
            x0, y0, x1, y1 = ed.get_carets()[0]
            s = ed.get_text_line(y0)
            ed.set_caret(len(s), y0)
            msg('insertion mode, at line end')
            return False

        if text=='i':
            self.insert = True
            self.update_caret()
            msg('insertion mode, at current char')
            return False

        if text=='I':
            self.insert = True
            self.update_caret()
            x0, y0, x1, y1 = ed.get_carets()[0]
            goto_first_nonspace_char(y0)
            msg('insertion mode, at 1st non-space char')
            return False

        if text=='^':
            x0, y0, x1, y1 = ed.get_carets()[0]
            goto_first_nonspace_char(y0)
            msg('go to 1st non-space char')
            return False

        if text=='x':
            ed.cmd(cc.cCommand_KeyDelete)
            msg('delete char')
            return False

        if text=='X':
            ed.cmd(cc.cCommand_KeyBackspace)
            msg('delete char left')
            return False

        if text=='r':
            self.replace_char = True
            msg('replace char to')
            return False

        if text=='R':
            self.insert = True
            self.update_caret()
            ed.set_prop(PROP_INSERT, False)
            msg('replace mode for current line')
            return False

        if text=='O':
            ed.cmd(cc.cCommand_TextInsertEmptyAbove)
            self.insert = True
            self.update_caret()
            msg('insert line above, insertion mode')
            return False

        if text=='o':
            ed.cmd(cc.cCommand_TextInsertEmptyBelow)
            self.insert = True
            self.update_caret()
            msg('insert line below, insertion mode')
            return False

        if text=='D':
            ed.cmd(cc.cCommand_TextDeleteToLineEnd)
            msg('delete to end of line')
            return False

        if text=='C':
            ed.cmd(cc.cCommand_TextDeleteToLineEnd)
            msg('change to end of line')
            self.insert = True
            self.update_caret()
            return False

        if text=='c':
            self.prefix_c = True
            msg('change?')
            return False

        if text=='d':
            self.prefix_d = True
            msg('delete?')
            return False

        if text in ['v', 'V']:
            x0, y0, x1, y1 = ed.get_carets()[0]
            self.visual = True
            self.visual_lines = text=='V'
            self.visual_start = (x0, y0)
            self.update_caret()
            s = 'visual mode'
            if self.visual_lines:
                s += ', by lines'
                ed.set_caret(0, y0, len(ed.get_text_line(y0)), y0)
            msg(s)
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

        if text==' ':
            ed.cmd(cc.cCommand_KeyRight)
            msg('move right')
            return False

        if text=='$':
            x0, y0, x1, y1 = ed.get_carets()[0]
            s = ed.get_text_line(y0)
            ed.set_caret(len(s), y0)
            msg('move to line end')
            return False

        #block all text in command mode
        msg('key not handled')
        return False
