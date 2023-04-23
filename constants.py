# Channels Modes
CHANNELS_RGB = 3
CHANNELS_RGBA = 4

"""
The colorspace in this qoi_desc is an enum where
  0 = sRGB, i.e. gamma scaled RGB channels and a linear alpha channel
  1 = all channels are linear
You may use the constants QOI_SRGB or QOI_LINEAR. The colorspace is purely
informative. It will be saved to the file header, but does not affect
how chunks are en-/decoded.
"""
# Colorspaces
QOI_SRGB = 0
QOI_LINEAR = 1

# chunk tags
QOI_OP_INDEX = 0x00  # 00xxxxxx
QOI_OP_DIFF = 0x40  # 01xxxxxx
QOI_OP_LUMA = 0x80  # 10xxxxxx
QOI_OP_RUN = 0xC0  # 11xxxxxx
QOI_OP_RGB = 0xFE  # 11111110
QOI_OP_RGBA = 0xFF  # 11111111
QOI_MASK_2 = 0xC0  # 11000000

# QOI file magic number 'qoif'
QOI_MAGIC = ord("q") << 24 | ord("o") << 16 | ord("i") << 8 | ord("f")

QOI_HEADER_SIZE = 14

# 2GB is the max file size that this implementation can safely handle. We guard
# against anything larger than that, assuming the worst case with 5 bytes per
# pixel, rounded down to a nice clean value. 400 million pixels ought to be
# enough for anybody.
QOI_PIXELS_MAX = 400000000

# The byte stream's end is marked with 7 0x00 bytes followed by a single 0x01 byte.
QOI_PADDING = [0 for _ in range(7)] + [1]
