import string
from cudatext import *
import cudatext_cmd as cc
import cudatext_keys as ck
from .text_func import *
from .scrollto import *

INI = 'plugins.ini' # without path - in 'settings' dir
ST_TAG = app_proc(PROC_GET_UNIQUE_TAG, '') # tag value must be >20

def msg(s):
    msg_status('[Vim] '+s)


class Command:
    active = False
    active_was = False
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
    prefix_j = False
    prefix_df = False
    prefix_z = False
    prefix_Z = False
    number = ''
    caret_normal = (2, -100, False)
    find_str = ''
    find_fw = True
    saved_prefix = ''
    saved_text = ''
    clip_full_line = False


    def __init__(self):

        self.remap_esc = ini_read(INI, 'vim_mode', 'remap_esc', '')

    def on_start(self, ed_self):

        op = ini_read(INI, 'vim_mode', 'on_start', '')
        if op=='c':
            self.toggle_active(False, False)
        elif op=='i':
            self.toggle_active(True, False)


    def get_status_info(self):

        if self.insert:
            return ('Insert', 0x0000B0)
        elif self.visual:
            return ('Visual', 0x800000 if self.visual_lines else 0x800080 )
        else:
            return ('Command', 0x808000)


    def update_caret(self):
        if self.insert or not self.active:
            value = self.caret_normal
        elif self.visual:
            value = (-100, -50, False)
        else:
            value = (-100, -100, True)
        ed.set_prop(PROP_CARET_VIEW, value)

        self.update_statusbar(False)


    def update_statusbar(self, delete_vim_cell):

        info, color = self.get_status_info()
        h_bar = 'main'

        if self.active:
            if delete_vim_cell:
                statusbar_proc(h_bar, STATUSBAR_DELETE_CELL, tag=ST_TAG)

            statusbar_proc(h_bar, STATUSBAR_ADD_CELL, index=-1, tag=ST_TAG)
            statusbar_proc(h_bar, STATUSBAR_SET_CELL_AUTOSIZE, value=True, tag=ST_TAG)
            statusbar_proc(h_bar, STATUSBAR_SET_CELL_TEXT, value='--'+info+'--', tag=ST_TAG)
        else:
            statusbar_proc(h_bar, STATUSBAR_DELETE_CELL, tag=ST_TAG)

        for i in range(statusbar_proc(h_bar, STATUSBAR_GET_COUNT)):
            statusbar_proc(h_bar, STATUSBAR_SET_CELL_COLOR_BACK, value=color if self.active else COLOR_NONE, index=i)
            statusbar_proc(h_bar, STATUSBAR_SET_CELL_COLOR_FONT, value=0xFFFFFF if self.active else COLOR_NONE, index=i)


    def toggle_active(self, insert=False, save_op=True):
        self.insert = insert
        self.active_was = True
        self.active = not self.active
        if self.active:
            self.caret_normal = ed.get_prop(PROP_CARET_VIEW)
            msg('plugin activated')
        else:
            msg('plugin deactivated')
        self.update_caret()

        if not self.active:
            if ini_read(INI, 'vim_mode', 'on_start', ''):
                res = msg_box('Turn off Vim Mode permanently (don\'t use after CudaText restart)?',
                    MB_OKCANCEL+MB_ICONQUESTION)
                if res==ID_OK:
                    ini_write(INI, 'vim_mode', 'on_start', '')

        elif save_op:
            res = msg_box('Make Vim Mode persistent, ie active after CudaText restart?\n\n'+
                          'Yes: persistent, start in command mode\n'+
                          'No: persistent, start in insertion mode\n'+
                          'Cancel: not persistent',
                MB_YESNOCANCEL+MB_ICONQUESTION)
            if res==ID_YES: op = 'c'
            if res==ID_NO: op = 'i'
            if res==ID_CANCEL: op = ''
            ini_write(INI, 'vim_mode', 'on_start', op)


    def on_open(self, ed_self):
        if not self.active_was:
            return
        self.update_caret()


    def use_visual(self):
        if not self.visual:
            return
        xx, yy = self.visual_start
        x0, y0, x1, y1 = ed.get_carets()[0]

        if self.visual_lines:
            if y0<yy:
                x0 = 0
                xx = 0
            else:
                xx = 0
                if x0>0:
                    x0 = 0
                    y0 += 1

        ed.set_caret(x0, y0, xx, yy)

        #s = 'visual selection'
        #if self.visual_lines:
        #    s += ', by lines'
        #msg(s)


    def do_esc(self):

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
            self.prefix_c = False
            self.prefix_d = False
            self.prefix_df = False
            self.prefix_g = False
            self.prefix_f = False
            self.prefix_j = False
            self.prefix_z = False
            self.prefix_Z = False
            msg('Esc')
            return


    def on_key(self, ed_self, key, state):
        if not self.active:
            return

        if state=='c':
            # Ctrl+H --> Backspace
            if key==ord('H'):
                ed_self.cmd(cc.cCommand_KeyBackspace)
                msg('BackSpace key')
                return False

            # Ctrl+I --> Tab char
            if key==ord('I'):
                ed_self.cmd(cc.cCommand_KeyTab)
                msg('Tab key')
                return False

            # Ctrl+J or Ctrl+M --> Enter
            if key in [ord('J'), ord('M')]:
                ed_self.cmd(cc.cCommand_KeyEnter)
                msg('Enter key')
                return False

            # Ctrl+[ --> Esc
            if key==219:
                ed_self.cmd(cc.cCommand_Cancel)
                self.do_esc()
                return False

            if key == ord('F'):
                ed_self.cmd(cc.cCommand_KeyPageDown)
                msg('f key')
                return False

            if key == ord('B'):
                ed_self.cmd(cc.cCommand_KeyPageUp)
                msg('b key')
                return False

        if key==ck.VK_ESCAPE:
            self.do_esc()

        if self.insert:
            if ed.get_prop(PROP_INSERT):
                msg('insertion mode')
            else:
                msg('replace mode')
            return

        if key==ck.VK_BACKSPACE:
            goto_l()
            msg('move left')
            return False

        if key in [
                ck.VK_LEFT, ck.VK_RIGHT,
                ck.VK_UP, ck.VK_DOWN,
                ck.VK_PAGEUP, ck.VK_PAGEDOWN,
                ck.VK_HOME, ck.VK_END,
                ] and state=='':
            if self.visual:
                if key==ck.VK_LEFT:
                    ed.cmd(cc.cCommand_KeyLeft_Sel)
                elif key==ck.VK_RIGHT:
                    ed.cmd(cc.cCommand_KeyRight_Sel)
                elif key==ck.VK_UP:
                    ed.cmd(cc.cCommand_KeyUp)
                elif key==ck.VK_DOWN:
                    ed.cmd(cc.cCommand_KeyDown)
                elif key==ck.VK_PAGEUP:
                    ed.cmd(cc.cCommand_KeyPageUp)
                elif key==ck.VK_PAGEDOWN:
                    ed.cmd(cc.cCommand_KeyPageDown)
                elif key==ck.VK_HOME:
                    ed.cmd(cc.cCommand_KeyHome)
                elif key==ck.VK_END:
                    ed.cmd(cc.cCommand_KeyEnd)

                self.use_visual()
                return False
            else:
                msg('movement key')
                return


    def handle(self, prefix, text):
        """Command processor"""

        self.saved_prefix = prefix
        self.saved_text = text
        x0, y0, x1, y1 = ed.get_carets()[0]

        if prefix=='r':
            ed.replace(x0, y0, x0+len(text), y0, text)
            msg('replaced char to: '+text)
            return

        if prefix in ('f', 'df'):
            if find_text_in_line(x0, y0, text,
                    self.prefix_f_fw,
                    self.prefix_f_before,
                    prefix=='df'
                    ):
                msg('found: '+text)
            else:
                msg('not found in line: '+text)
            return

        if prefix=='g':
            ed.cmd(cc.cCommand_GotoTextBegin)
            msg('go to text begin')
            return

        if prefix=='z':
            if text=='z':
                do_scroll('center')
                msg('scroll to center')
            elif text=='.':
                do_scroll('center_nblank')
                msg('scroll to center, first non-blank')
            elif text=='t':
                do_scroll('top')
                msg('scroll to top')
            elif text=='b':
                do_scroll('btm')
                msg('scroll to bottom')
            else:
                msg('unknown command')
            return

        if prefix=='d':
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
                    res = find_text_pos(x0, y0, s)
                    if res:
                        x1, y1 = res
                        ed.delete(x0, y0, x1, y1)
                        msg('delete to text: '+s)
                    else:
                        msg('not found: '+s)
                else:
                    msg('Esc')
            return

        if prefix=='Z':
            if text=='Z':
                ed.cmd(cc.cmd_FileSave)
                ed.cmd(cc.cmd_FileExit)
                msg('quit with saving')
            elif text=='Q':
                ed.set_prop(PROP_MODIFIED, False)
                ed.cmd(cc.cmd_FileExit)
                msg('quit without saving')
            return

        if prefix=='':
            if text=='h':
                goto_l()
                msg('left')
                self.use_visual()
                return

            if text=='j':
                ed.cmd(cc.cCommand_KeyDown)
                msg('down')
                self.use_visual()
                return

            if text=='k':
                ed.cmd(cc.cCommand_KeyUp)
                msg('up')
                self.use_visual()
                return

            if text=='l':
                goto_r()
                msg('right')
                self.use_visual()
                return

            if text in ('b', 'B'):
                ed.cmd(cc.cCommand_GotoWordPrev)
                msg('go to prev word')
                self.use_visual()
                return

            if text in ['w', 'W']:
                ed.cmd(cc.cCommand_GotoWordNext)
                msg('go to next word')
                self.use_visual()
                return

            if text in ['e', 'E']:
                goto_word_end()
                msg('go to word end')
                self.use_visual()
                return

            if text=='^':
                goto_first_nonspace_char(y0)
                msg('go to 1st non-space char')
                self.use_visual()
                return

            if text=='-':
                if y0>0:
                    goto_first_nonspace_char(y0-1)
                    msg('go to 1st non-space char, at prev line')
                self.use_visual()
                return

            if text=='+':
                if y0<ed.get_line_count()-1:
                    goto_first_nonspace_char(y0+1)
                    msg('go to 1st non-space char, at next line')
                self.use_visual()
                return

            if text=='x':
                ed.cmd(cc.cCommand_KeyDelete)
                msg('delete char')
                self.use_visual()
                return

            if text=='X':
                ed.cmd(cc.cCommand_KeyBackspace)
                msg('delete char left')
                self.use_visual()
                return

            if text=='O':
                ed.cmd(cc.cCommand_TextInsertEmptyAbove)
                self.insert = True
                self.update_caret()
                msg('insert line above, insertion mode')
                return

            if text=='o':
                ed.cmd(cc.cCommand_TextInsertEmptyBelow)
                self.insert = True
                self.update_caret()
                msg('insert line below, insertion mode')
                return

            if text=='D':
                ed.cmd(cc.cCommand_TextDeleteToLineEnd)
                msg('delete to end of line')
                self.use_visual()
                return

            if text=='C':
                ed.cmd(cc.cCommand_TextDeleteToLineEnd)
                msg('change to end of line')
                self.insert = True
                self.update_caret()
                return

            if text=='d':
                if ed.get_text_sel():
                    self.clip_full_line = self.visual and self.visual_lines
                    self.visual = False
                    self.update_caret()
                    ed.cmd(cc.cCommand_ClipboardCut)
                    msg('cut selection')
                    self.use_visual()
                return

            if text==' ':
                goto_r()
                msg('move right')
                self.use_visual()
                return

            if text=='$':
                goto_after_line()
                msg('move to line end')
                self.use_visual()
                return

            if text in ('n', 'N'):
                s = self.find_str
                if s:
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
                self.use_visual()
                return


            if text=='u':
                ed.cmd(cc.cCommand_Undo)
                msg('undo')
                return

            if text=='y':
                if y1<0:
                    msg('text not selected')
                    return
                self.clip_full_line = self.visual and self.visual_lines

                xx0, yy0, xx1, yy1 = x0, y0, x1, y1
                if (yy0, xx0)>(yy1, xx1):
                    xx0, yy0, xx1, yy1 = xx1, yy1, xx0, yy0
                    if self.visual:
                        xx1 += 1 # like Vim
                s = ed.get_text_substr(xx0, yy0, xx1, yy1)
                app_proc(PROC_SET_CLIP, s)

                msg('copy/yank'+ (', full line(s)' if self.clip_full_line else ''))

                self.visual = False
                self.update_caret()
                return

            if text=='Y':
                self.visual = False
                self.update_caret()

                s = ed.get_text_line(y0)+'\n'
                app_proc(PROC_SET_CLIP, s)
                self.clip_full_line = True
                msg('copy/yank entire line')
                return

            if text=='p':
                self.visual = False
                self.update_caret()

                if self.clip_full_line:
                    #ed.cmd(cc.cCommand_TextInsertEmptyBelow)
                    if y0>=ed.get_line_count()-1:
                        ed.set_text_line(-1, '')
                    ed.set_caret(0, y0+1, -1, -1)
                else:
                    goto_r()
                ed.cmd(cc.cCommand_ClipboardPaste_KeepCaret)

                msg('paste, after caret')
                self.use_visual()
                return

            if text=='P':
                self.visual = False
                self.update_caret()

                ed.cmd(cc.cCommand_ClipboardPaste_KeepCaret)
                msg('paste, before caret')
                self.use_visual()
                return

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
                return

            if text=='J':
                join_line_with_next()
                msg('join with next line')
                return

            if text=='#':
                if goto_next_word_match():
                    msg('found next match')
                else:
                    msg('not found next match')
                self.use_visual()
                return

            if text=='H':
                ed.cmd(cc.cCommand_GotoScreenTop)
                msg('go to screen top')
                self.use_visual()
                return

            if text=='L':
                ed.cmd(cc.cCommand_GotoScreenBottom)
                msg('go to screen bottom')
                self.use_visual()
                return

            if text=='M':
                ed.cmd(cc.cCommand_GotoScreenCenter)
                msg('go to screen middle')
                self.use_visual()
                return

            if text=='S':
                ed.set_caret(0, y0)
                ed.set_text_line(y0, '')
                self.insert = True
                self.update_caret()
                msg('substitute entire line')
                return



    def on_insert(self, ed_self, text):
        if not self.active:
            return

        if self.insert:
            if self.prefix_j and text==self.remap_esc:
                self.prefix_j = False
                ed_self.cmd(cc.cCommand_KeyBackspace)
                self.on_key(ed_self, ck.VK_ESCAPE, '')
                return False
            self.prefix_j = self.remap_esc and text=='j' and ed_self.get_prop(PROP_INSERT)
            return

        if self.replace_char:
            self.replace_char = False
            self.handle('r', text)
            return False

        if self.prefix_f:
            self.prefix_f = False
            self.handle('f', text)

            if self.visual:
                self.use_visual()
            return False

        if self.prefix_Z:
            self.prefix_Z = False
            self.handle('Z', text)
            return False

        if self.prefix_df:
            self.handle('df', text)

            if self.prefix_c:
                self.insert = True
                self.update_caret()

            self.prefix_c = False
            self.prefix_d = False
            self.prefix_df = False
            return False

        x0, y0, x1, y1 = ed.get_carets()[0]
        if text in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
            use_num = True
            if text=='0' and self.number=='':
                use_num = False
                ed.set_caret(0, y0)
                msg('moved to line begin')
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
                self.handle('g', '')
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
                    ed.set_caret(x0, index)
                    ed.cmd(cc.cCommand_ScrollToCaretTop)
                    msg('go to line '+self.number)
                else:
                    msg('incorrect line number: '+self.number)
                self.number = ''
            return False


        if self.prefix_c or self.prefix_d:

            if text in ('f', 'F', 't', 'T'):
                self.prefix_df = True
                self.prefix_f_fw = text in ('f', 't')
                self.prefix_f_before = text in ('t', 'T')
                msg('delete until what?')
                return False

            self.handle('d', text)
            if self.prefix_c:
                self.insert = True
                self.update_caret()
            self.prefix_c = False
            self.prefix_d = False
            return False


        if self.prefix_z:
            self.handle('z', text)
            self.prefix_z = False
            return False

        if text in ('h', 'j', 'k', 'l',
                    'b', 'B', 'w', 'W', 'e', 'E',
                    'x', 'X', 'o', 'O',
                    'n', 'N', 'u', 'y', 'Y', 'p', 'P',
                    'D', 'C', 'J',
                    'H', 'L', 'M', 'S',
                    '^', '-', '+', ' ', '$', '~', '#',
                    ):
            self.handle('', text)
            return False


        if text=='a':
            s = ed.get_text_line(y0)
            if x0<len(s):
                goto_r()
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


        if text=='c':
            self.prefix_c = True
            msg('change?')
            return False

        if text=='d':
            if ed.get_text_sel():
                self.handle('', text)
            else:
                self.prefix_d = True
                msg('delete?')
            self.use_visual()
            return False

        if text=='z':
            self.prefix_z = True
            msg('scroll to?')
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
                ed.set_caret(0, y0, 0, y0+1)
            msg(s)
            return False


        if text=='|':
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
            self.use_visual()
            return False


        if text=='/':
            s = dlg_input('Search forward:', '')
            if s:
                self.find_str = s
                self.find_fw = True
                res = find_text_pos(x0+1, y0, s)
                if res:
                    x1, y1 = res
                    ed.set_caret(x1, y1)
                    msg('found: '+s)
                else:
                    msg('not found: '+s)
            else:
                msg('Esc')
            self.use_visual()
            return False

        if text=='?':
            s = dlg_input('Search backward:', '')
            if s:
                self.find_str = s
                self.find_fw = False
                res = find_text_pos_backward(x0, y0, s)
                if res:
                    x1, y1 = res
                    ed.set_caret(x1, y1)
                    msg('found: '+s)
                else:
                    msg('not found: '+s)
            else:
                msg('Esc')
            self.use_visual()
            return False

        if text=='.':
            self.handle(self.saved_prefix, self.saved_text)
            return False

        if text=='Z':
            self.prefix_Z = True
            msg('quit?')
            return False


        #block all text in command mode
        msg('unknown command')
        return False


    def config_esc(self):

        res = dlg_input('Remap Esc to j<smth>. E.g. for command "jk" enter "k". Empty - no remap.', self.remap_esc)
        if res is None:
            return
        if res and res not in string.ascii_letters:
            msg_box('Input "%s" is not valid, please enter single letter'%res, MB_OK+MB_ICONERROR)
            return
        self.remap_esc = res
        ini_write(INI, 'vim_mode', 'remap_esc', res)


    def on_state(self, ed_self, state):

        if not self.active_was:
            return

        # must refresh statusbar after Options Editor has changed options
        if state==APPSTATE_CONFIG_REREAD:
            self.update_statusbar(True)
