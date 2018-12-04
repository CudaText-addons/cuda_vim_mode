from cudatext import *

def do_scroll(what):

    def get_pos(y, h):
        if what=='cnt':
            return max(0, y-h//2)
        elif what=='top':
            return y
        elif what=='btm':
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
