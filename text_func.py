from cudatext import *
import cudatext_cmd as cc
import string

WORD_CHARS = string.ascii_letters + string.digits + '_'

def get_word_info(x0, y0):
    text = ed.get_text_line(y0)
    if not text:
        return (x0, y0, 0, '')
    if x0>len(text):
        x0 = len(text)

    x1 = x0
    while x1>0 and text[x1-1] in WORD_CHARS: x1-=1
    x2 = x0
    while x2<len(text) and text[x2] in WORD_CHARS: x2+=1

    return (x1, y0, x2-x1, text[x1:x2])


def goto_word_end():
    x0, y0, x1, y1 = ed.get_carets()[0]
    s = ed.get_text_line(y0)
    if not (0<=x0<len(s)):
        return

    on_word = s[x0] in WORD_CHARS
    if not on_word:
        ed.cmd(cc.cCommand_GotoWordNext)
        x0, y0, x1, y1 = ed.get_carets()[0]

    info = get_word_info(x0, y0)
    if not info: return
    xw, yw, nlen, str = info

    #at word end already?
    if xw+nlen-1 == x0:
        ed.cmd(cc.cCommand_KeyRight)
        ed.cmd(cc.cCommand_GotoWordNext)
        x0, y0, x1, y1 = ed.get_carets()[0]

        info = get_word_info(x0, y0)
        if not info: return
        xw, yw, nlen, str = info

    ed.set_caret(xw+nlen-1, yw)


def find_text_pos(x0, y0, text):

    for nline in range(y0, ed.get_line_count()):
        if nline==y0:
            x_start = x0
        else:
            x_start = 0

        sline = ed.get_text_line(nline)
        npos = sline.find(text, x_start)
        if npos>=0:
            return (npos, nline)


def find_text_pos_backward(x0, y0, text):

    for nline in range(y0, -1, -1):
        sline = ed.get_text_line(nline)

        if nline==y0:
            x_start = x0
        else:
            x_start = len(sline)

        npos = sline.rfind(text, 0, x_start)
        if npos>=0:
            return (npos, nline)


def goto_first_nonspace_char(nline):
    s = ed.get_text_line(nline)
    x = 0
    while x<len(s) and s[x] in (' ', '\t'):
        x += 1
    ed.set_caret(x, nline)


def find_text_in_line(x0, y0, text, next, before):
    sline = ed.get_text_line(y0)
    if not sline: return

    if next:
        n = sline.find(text, x0+1)
    else:
        n = sline.rfind(text, 0, x0)

    if n>=0:
        if before:
            if next:
                n -= 1
            else:
                n += 1
        ed.set_caret(n, y0)
        return True


