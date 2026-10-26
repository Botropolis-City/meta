"""A 1920x1080 at 60 Hz EDID, so the soak box's iGPU drives a display nobody plugged in (item 245).

The kernel dropped its built-in EDIDs, so drm.edid_firmware needs a file of its own.
"""

HEADER = bytes([0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00])


def _manufacturer(code):
    a, b, c = (ord(ch) - ord('A') + 1 for ch in code)
    value = a << 10 | b << 5 | c
    return bytes([value >> 8, value & 0xFF])


def _detailed_timing():
    clock = 14850
    h_active, h_blank, h_front, h_sync = 1920, 280, 88, 44
    v_active, v_blank, v_front, v_sync = 1080, 45, 4, 5
    width_mm, height_mm = 531, 299
    return bytes([
        clock & 0xFF, clock >> 8,
        h_active & 0xFF, h_blank & 0xFF, (h_active >> 8) << 4 | h_blank >> 8,
        v_active & 0xFF, v_blank & 0xFF, (v_active >> 8) << 4 | v_blank >> 8,
        h_front & 0xFF, h_sync & 0xFF, (v_front & 0x0F) << 4 | v_sync & 0x0F,
        (h_front >> 8) << 6 | (h_sync >> 8) << 4 | (v_front >> 4) << 2 | v_sync >> 4,
        width_mm & 0xFF, height_mm & 0xFF, (width_mm >> 8) << 4 | height_mm >> 8,
        0, 0, 0x1E,
    ])


def _descriptor(tag, payload):
    return bytes([0, 0, 0, tag, 0]) + payload


def _text(text):
    raw = text.encode('ascii')[:13]
    return raw + (b'\n' + b' ' * 12)[:13 - len(raw)]


def edid_1080p():
    base = (
        HEADER
        + _manufacturer('BTP')
        + bytes([0x01, 0x00, 0, 0, 0, 0, 1, 2026 - 1990])
        + bytes([1, 3])
        + bytes([0x80, 53, 30, 120, 0x0E])
        + bytes([0xEE, 0x91, 0xA3, 0x54, 0x4C, 0x99, 0x26, 0x0F, 0x50, 0x54])
        + bytes([0, 0, 0])
        + bytes([0xD1, 0xC0]) + bytes([0x01, 0x01]) * 7
        + _detailed_timing()
        + _descriptor(0xFD, bytes([56, 76, 30, 83, 17, 0]) + b'\n' + b' ' * 6)
        + _descriptor(0xFC, _text('botropolis'))
        + _descriptor(0x10, bytes(13))
        + bytes([0])
    )
    return base + bytes([(256 - sum(base) % 256) % 256])


if __name__ == '__main__':
    import sys
    sys.stdout.buffer.write(edid_1080p())
