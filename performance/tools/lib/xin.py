"""usage: xin.py [--asked-screen] move X Y | wheel N | key NAME | resize WINDOW W H | frame PATH

XTEST input through libX11 and libXtst, by ctypes: moves the real pointer
to X,Y, turns the real wheel N notches (in when N > 0, out when N < 0), or
presses and releases the key named by its X keysym (Escape, a, Return), so
a focused window gets the input a hand would give it. resize moves WINDOW
(an id, decimal or 0x hex) to 0,0 at W by H, for a display with no window
manager to size it, such as a private Xvfb. frame writes the root window
to PATH as a PNG and prints its mean luminance, 0-255, as "luma L".

It refuses an empty DISPLAY, :0 or :0.0, which may be someone's screen,
and exits 2 before it opens anything, unless this machine is the soak box,
whose set-up writes /etc/botropolis-soak-box (PERF_XIN_BOX_MARK moves it,
for tests), or --asked-screen says the person at the screen was asked for
it, as perf-fitzoom's run asks Aria (item 321).
"""
import ctypes
import os
import struct
import sys
import time
import zlib

BOX_MARK = '/etc/botropolis-soak-box'
SCREENS = ('', ':0', ':0.0')


def refusal(display, box, asked_screen):
    if box or asked_screen or display.strip() not in SCREENS:
        return None
    return ("xin.py refuses display %r: it may be someone's screen; only the soak box (%s) or a run that asked "
            "for the screen (--asked-screen) may use it" % (display, BOX_MARK))


def bgrx_to_rgb(row, width):
    rgb = bytearray(width * 3)
    rgb[0::3] = row[2:width * 4:4]
    rgb[1::3] = row[1:width * 4:4]
    rgb[2::3] = row[0:width * 4:4]
    return bytes(rgb)


def mean_luma(width, rows):
    r = g = b = 0
    for row in rows:
        r, g, b = r + sum(row[0::3]), g + sum(row[1::3]), b + sum(row[2::3])
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / (width * len(rows))


def png(width, height, rows):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    raw = b''.join(b'\x00' + row for row in rows)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b''))


class XImage(ctypes.Structure):
    _fields_ = [('width', ctypes.c_int), ('height', ctypes.c_int), ('xoffset', ctypes.c_int),
                ('format', ctypes.c_int), ('data', ctypes.c_void_p), ('byte_order', ctypes.c_int),
                ('bitmap_unit', ctypes.c_int), ('bitmap_bit_order', ctypes.c_int), ('bitmap_pad', ctypes.c_int),
                ('depth', ctypes.c_int), ('bytes_per_line', ctypes.c_int), ('bits_per_pixel', ctypes.c_int)]


def frame(x, d, path):
    x.XDefaultRootWindow.restype = ctypes.c_ulong
    root = x.XDefaultRootWindow(d)
    screen = x.XDefaultScreen(d)
    width, height = x.XDisplayWidth(d, screen), x.XDisplayHeight(d, screen)
    x.XGetImage.restype = ctypes.POINTER(XImage)
    x.XGetImage.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_int, ctypes.c_uint,
                            ctypes.c_uint, ctypes.c_ulong, ctypes.c_int]
    image = x.XGetImage(d, root, 0, 0, width, height, 0xffffffff, 2)
    if not image:
        sys.exit('could not read the root window')
    img = image.contents
    if img.bits_per_pixel != 32:
        sys.exit('frame needs 32 bits a pixel, and the display has %d' % img.bits_per_pixel)
    data = ctypes.string_at(img.data, img.bytes_per_line * img.height)
    rows = [bgrx_to_rgb(data[y * img.bytes_per_line:(y + 1) * img.bytes_per_line], img.width)
            for y in range(img.height)]
    with open(path, 'wb') as f:
        f.write(png(img.width, img.height, rows))
    print('luma %.1f' % mean_luma(img.width, rows))


def main(argv):
    if len(argv) < 2 or argv[1] in ('-h', '--help'):
        print(__doc__)
        return 0
    asked_screen = argv[1] == '--asked-screen'
    if asked_screen:
        argv = argv[:1] + argv[2:]
    refused = refusal(os.environ.get('DISPLAY', ''), os.path.exists(os.environ.get('PERF_XIN_BOX_MARK', BOX_MARK)),
                      asked_screen)
    if refused:
        sys.stderr.write(refused + '\n')
        return 2
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
    elif argv[1] == 'key' and len(argv) == 3:
        x.XStringToKeysym.restype = ctypes.c_ulong
        sym = x.XStringToKeysym(argv[2].encode())
        if not sym:
            sys.exit('no keysym %s' % argv[2])
        code = x.XKeysymToKeycode(d, ctypes.c_ulong(sym))
        t.XTestFakeKeyEvent(d, code, 1, 0)
        t.XTestFakeKeyEvent(d, code, 0, 0)
    elif argv[1] == 'resize' and len(argv) == 5:
        x.XMoveResizeWindow(d, ctypes.c_ulong(int(argv[2], 0)), 0, 0, int(argv[3]), int(argv[4]))
    elif argv[1] == 'frame' and len(argv) == 3:
        frame(x, d, argv[2])
    else:
        sys.exit(__doc__)
    x.XFlush(d)
    x.XCloseDisplay(d)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
