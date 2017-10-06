from cudatext import *
import cudatext_cmd as cc
import cudatext_keys as ck
from .text_func import *

INI = 'cuda_vim_mode.ini'

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
    prefix_f = False
    prefix_f_fw = True
    prefix_f_before = False
    number = ''
    caret_normal = 2
    find_str = ''
    find_fw = True


    def on_start(self, ed_self):
        op = ini_read(INI, 'op', 'on_start', '')
        if op=='c':
            self.toggle_active(False, False)
        elif op=='i':
            self.toggle_active(True, False)


    def update_caret(self):
        if self.insert or not self.active:
            value = self.caret_normal
        elif self.visual:
            value = 25
        else:
            value = 26
        ed.set_prop(PROP_CARET_SHAPE, value)


    def toggle_active(self, insert=False, save_op=True):
        self.insert = insert
        self.active = not self.active
        if self.active:
            self.caret_normal = ed.get_prop(PROP_CARET_SHAPE)
            msg('plugin activated')
        else:
            msg('plugin deactivated')
        self.update_caret()

        if save_op:
            res = msg_box('Make Vim Mode persistent, ie active after CudaText restart?\n\n'+
                          'Yes: persistent, start in command mode\n'+
                          'No: persistent, start in insertion mode\n'+
                          'Cancel: not persistent',
                MB_YESNOCANCEL+MB_ICONQUESTION)
            if res==ID_YES: op = 'c'
            if res==ID_NO: op = 'i'
            if res==ID_CANCEL: op = ''
            ini_write(INI, 'op', 'on_start', op)


    def on_open(self, ed_self):
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
                self.prefix_f = False
                msg('Esc')
                return

        if self.insert:
            if ed.get_prop(PROP_INSERT):
                msg('insertion mode')
            else:
                msg('replace mode')
            return

        if key==ck.VK_BACKSPACE:
            ed.cmd(cc.cCommand_KeyLeft)
            msg('move left')
            return False

        if key in [
                ck.VK_LEFT, ck.VK_RIGHT,
                ck.VK_UP, ck.VK_DOWN,
                ck.VK_PAGEUP, ck.VK_PAGEDOWN,
                ck.VK_HOME, ck.VK_END,
                ord('H'), ord('J'), ord('K'), ord('L')
                ] and state=='':
            if self.visual:
                xx, yy = self.visual_start
                x0, y0, x1, y1 = ed.get_carets()[0]
                y_max = ed.get_line_count()-1

                if key in (ck.VK_LEFT, ord('H')):
                    ed.cmd(cc.cCommand_KeyLeft)
                elif key in (ck.VK_RIGHT, ord('L')):
                    ed.cmd(cc.cCommand_KeyRight)
                elif key in (ck.VK_UP, ord('K')):
                    ed.cmd(cc.cCommand_KeyUp)
                elif key in (ck.VK_DOWN, ord('J')):
                    ed.cmd(cc.cCommand_KeyDown)
                elif key==ck.VK_PAGEUP:
                    ed.cmd(cc.cCommand_KeyPageUp)
                elif key==ck.VK_PAGEDOWN:
                    ed.cmd(cc.cCommand_KeyPageDown)
                elif key==ck.VK_HOME:
                    ed.cmd(cc.cCommand_KeyHome)
                elif key==ck.VK_END:
                    ed.cmd(cc.cCommand_KeyEnd)

                x0, y0, x1, y1 = ed.get_carets()[0]

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

        if self.prefix_f:
            self.prefix_f = False
            x0, y0, x1, y1 = ed.get_carets()[0]
            if find_text_in_line(x0, y0, text,
                    self.prefix_f_fw,
                    self.prefix_f_before):
                msg('found: '+text)
            else:
                msg('not found in line: '+text)
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
                goto_word_end(True)
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
            goto_after_line()
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

        if text=='-':
            x0, y0, x1, y1 = ed.get_carets()[0]
            if y0>0:
                goto_first_nonspace_char(y0-1)
                msg('go to 1st non-space char, at prev line')
            return False

        if text=='+':
            x0, y0, x1, y1 = ed.get_carets()[0]
            if y0<ed.get_line_count()-1:
                goto_first_nonspace_char(y0+1)
                msg('go to 1st non-space char, at next line')
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
            if ed.get_text_sel():
                self.visual = False
                self.update_caret()
                ed.cmd(cc.cCommand_ClipboardCut)
                msg('cut selection')
            else:
                self.prefix_d = True
                msg('delete?')
            return False

        if text in ('f', 'F', 't', 'T'):
            self.prefix_f = True
            self.prefix_f_fw = text in ('f', 't')
            self.prefix_f_before = text in ('t', 'T')
            msg('find char?')
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
            goto_after_line()
            msg('move to line end')
            return False

        if text=='/':
            s = dlg_input('Search forward:', '')
            if s:
                self.find_str = s
                self.find_fw = True
                x0, y0, x1, y1 = ed.get_carets()[0]
                res = find_text_pos(x0+1, y0, s)
                if res:
                    x1, y1 = res
                    ed.set_caret(x1, y1)
                    msg('found: '+s)
                else:
                    msg('not found: '+s)
            else:
                msg('Esc')
            return False

        if text=='?':
            s = dlg_input('Search backward:', '')
            if s:
                self.find_str = s
                self.find_fw = False
                x0, y0, x1, y1 = ed.get_carets()[0]
                res = find_text_pos_backward(x0, y0, s)
                if res:
                    x1, y1 = res
                    ed.set_caret(x1, y1)
                    msg('found: '+s)
                else:
                    msg('not found: '+s)
            else:
                msg('Esc')
            return False

        if text in ('n', 'N'):
            s = self.find_str
            if s:
                x0, y0, x1, y1 = ed.get_carets()[0]
                #use xor to invert value
                is_next = self.find_fw ^ (text=='N')
                if is_next:
                    res = find_text_pos(x0+1, y0, s)
                else:
                    res = find_text_pos_backward(x0, y0, s)
                if res:
                    x1, y1 = res
                    ed.set_caret(x1, y1)
                    msg('found (%s): '%('next' if is_next else 'back') + s)
                else:
                    msg('not found: '+s)
            else:
                msg('search string not set')
            return False

        if text=='u':
            ed.cmd(cc.cCommand_Undo)
            msg('undo')
            return False

        if text=='y':
            self.visual = False
            self.update_caret()

            ed.cmd(cc.cCommand_ClipboardCopy)
            msg('copy/yank')
            return False

        if text=='Y':
            self.visual = False
            self.update_caret()

            ed.cmd(cc.cmd_CopyLine)
            msg('copy/yank entire line')
            return False

        if text=='p':
            self.visual = False
            self.update_caret()

            ed.cmd(cc.cCommand_KeyRight)
            ed.cmd(cc.cCommand_ClipboardPaste_KeepCaret)
            msg('paste, after caret')
            return False

        if text=='P':
            self.visual = False
            self.update_caret()

            ed.cmd(cc.cCommand_ClipboardPaste_KeepCaret)
            msg('paste, before caret')
            return False

        if text=='~':
            self.visual = False
            self.update_caret()

            if ed.get_text_sel():
                ed.cmd(cc.cCommand_TextCaseInvert)
                msg('invert case of selection')
            else:
                ed.cmd(cc.cCommand_KeyRight_Sel)
                ed.cmd(cc.cCommand_TextCaseInvert)
                msg('invert case of char')

            ed.cmd(cc.cCommand_SelectNone)
            return False

        if text=='J':
            goto_after_line()
            x0, y0, x1, y1 = ed.get_carets()[0]
            if y0>= ed.get_line_count()-1: return

            empty = ed.get_text_line(y0)=='' or ed.get_text_line(y0+1)==''
            if not empty:
                ed.cmd(cc.cCommand_TextInsert, ' ')

            ed.cmd(cc.cCommand_KeyDelete)
            msg('join with next line')
            return False

        if text=='#':
            if goto_next_word_match():
                msg('found next match')
            else:
                msg('not found next match')
            return False

        if text=='H':
            ed.cmd(cc.cCommand_GotoScreenTop)
            msg('go to screen top')
            return False

        if text=='L':
            ed.cmd(cc.cCommand_GotoScreenBottom)
            msg('go to screen bottom')
            return False

        if text=='M':
            ed.cmd(cc.cCommand_GotoScreenCenter)
            msg('go to screen middle')
            return False


        #block all text in command mode
        msg('key not handled')
        return False
