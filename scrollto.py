from cudatext import *

def do_scroll(what):

    def get_pos(y, h):
        if what=='center':
            # scroll line y to center
            newy = max(0, y-h//2)
            return newy
        elif what=='center_nblank':
            # same as 'center' but put caret on 1st nonblank char
            s = ed.get_text_line(y)
            newx = 0
            while newx<len(s) and (s[newx] in ' \t'):
                newx += 1
            ed.set_caret(newx, y)
            newy = max(0, y-h//2)
            return newy
        elif what=='top':
            # scroll line to top
            return y
        elif what=='btm':
            # scroll line to bottom
            return max(0, y-h)

    carets = ed.get_carets()
    if len(carets)!=1:
        return

    x, y, x1, y1 = carets[0]
    h = ed.get_prop(PROP_VISIBLE_LINES)
    pos = get_pos(y, h)

    if ed.get_prop(PROP_WRAP)!=0:
        w = ed.get_wrapinfo()
        for n in reversed(range(len(w))):
            wi = w[n]
            if wi['line']==y and wi['char']-1<=x:
                pos = get_pos(n, h)
                break

    ed.set_prop(PROP_SCROLL_VERT, pos)
