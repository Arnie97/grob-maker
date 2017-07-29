#!/usr/bin/env python3

import PIL.Image
from sys import argv
from codecs import encode
from itertools import zip_longest

SCREEN = (131, 64)
GROB = '''HP39AscD {name_len} {name}
MAKEGROB {grob_slot};%d %d {grob_hex}:
\->DISPLAY {grob_slot}:
FREEZE:''' % SCREEN


def split(iterable, group_size, padding=None):
    return zip_longest(*[iter(iterable)] * group_size, fillvalue=padding)


def image2pixels(im):
    if im.size != SCREEN:
        im = im.crop((0, 0) + SCREEN)  # crop to screen size

    im = im.convert('1')
    # im.show()
    pixels = im.getdata()
    return map(lambda x: 0 if x else 1, pixels)  # map 255 to 0


def pixels2bytes(pixels):
    for row in split(pixels, SCREEN[0]):
        for byte in split(row, 8, 0):
            yield sum(p[1] << p[0] for p in enumerate(byte))


def swap_nibbles(hex_data):
    return ''.join(map(
        lambda nibbles: nibbles[1] + nibbles[0],
        split(hex_data, 2)
    ))


def image2grob(im):
    grob_raw = bytes(pixels2bytes(image2pixels(im)))
    grob_hex = encode(grob_raw, 'hex').decode('ascii')
    grob_hex = swap_nibbles(grob_hex).upper()
    grob_slot = 'G0'
    name = argv[2]
    name_len = len(name)
    return GROB.format_map(locals())


if __name__ == '__main__':
    try:
        assert len(argv) == 3
        im = PIL.Image.open(argv[1])
        with open(argv[2], 'w') as f:
            print(image2grob(im), file=f)
    except AssertionError:
        print('Usage: %s <image-file> <grob-file>' % argv[0])
    except OSError as e:
        print(e)
