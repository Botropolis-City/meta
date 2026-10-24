"""usage: xin.py move X Y | wheel N

XTEST input through libX11 and libXtst, by ctypes: moves the real pointer
to X,Y, or turns the real wheel N notches (in when N > 0, out when N < 0),
so a focused window gets the input a hand would give it.
"""
import ctypes
import sys
import time


def main(argv):
    if len(argv) < 2 or argv[1] in ('-h', '--help'):
        print(__doc__)
        return 0
    x = ctypes.cdll.LoadLibrary('libX11.so.6')
    t = ctypes.cdll.LoadLibrary('libXtst.so.6')
    x.XOpenDisplay.restype = ctypes.c_void_p
    d = ctypes.c_void_p(x.XOpenDisplay(None))
    if not d:
        sys.exit('no display')
    if argv[1] == 'move' and len(argv) == 4:
        t.XTestFakeMotionEvent(d, -1, int(argv[2]), int(argv[3]), 0)
    elif argv[1] == 'wheel' and len(argv) == 3:
        n = int(argv[2])
        button = 4 if n > 0 else 5
        for _ in range(abs(n)):
            t.XTestFakeButtonEvent(d, button, 1, 0)
            t.XTestFakeButtonEvent(d, button, 0, 0)
            x.XFlush(d)
            time.sleep(0.15)
    else:
        sys.exit(__doc__)
    x.XFlush(d)
    x.XCloseDisplay(d)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
