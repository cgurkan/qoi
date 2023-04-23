from typing import Dict

from PIL import Image

from constants import *
from utils import ByteReader, Pixel


def decode_to_img(img_bytes: bytes, out_path: str) -> None:
    width, height, channels, colorspace, pixel_data = decode(img_bytes)

    mode = "RGBA" if channels == 4 else "RGB"
    size = (width, height)
    data = bytes(pixel_data)
    decoder_name = "raw"

    # Create a PIL Image from our pixel array.
    img = Image.frombuffer(mode=mode, size=size, data=data, decoder_name=decoder_name)
    img.save(out_path, "png")


# Read header
def qoiRead32(reader: ByteReader) -> int:
    data = [reader.read() for _ in range(4)]
    b1, b2, b3, b4 = data
    return b1 << 24 | b2 << 16 | b3 << 8 | b4


def decode(file_bytes: bytes) -> Dict:
    reader = ByteReader(file_bytes)
    header_magic = qoiRead32(reader)
    # Check if header is valid for QOI format
    if header_magic != QOI_MAGIC:
        raise ValueError("provided image does not contain QOI header")

    width = qoiRead32(reader)
    height = qoiRead32(reader)
    channels = reader.read()
    colorspace = reader.read()
    print("(D) Width: ", width)
    print("(D) Height:", height)
    print("(D) Channels:", channels)
    print("(D) ColorSpace:", colorspace)

    hash_array = [Pixel() for _ in range(64)]
    out_size = width * height * channels
    pixel_data = bytearray(out_size)
    px_value = Pixel()
    run = 0
    for i in range(-channels, out_size, channels):
        index_pos = px_value.hash
        hash_array[index_pos].update(px_value.bytes)

        if i >= 0:
            pixel_data[i : i + channels] = px_value.bytes

        if run > 0:
            run -= 1
            continue

        b1 = reader.read()
        if b1 is None:
            break

        if b1 == QOI_OP_RGB:
            new_value = bytes((reader.read() for _ in range(3)))
            px_value.update(new_value)
            continue

        if b1 == QOI_OP_RGBA:
            new_value = bytes((reader.read() for _ in range(4)))
            px_value.update(new_value)
            continue

        if (b1 & QOI_MASK_2) == QOI_OP_INDEX:
            px_value.update(hash_array[b1].bytes)
            continue

        if (b1 & QOI_MASK_2) == QOI_OP_DIFF:
            red = (px_value.red + ((b1 >> 4) & 0x03) - 2) % 256
            green = (px_value.green + ((b1 >> 2) & 0x03) - 2) % 256
            blue = (px_value.blue + (b1 & 0x03) - 2) % 256
            px_value.update(bytes((red, green, blue)))
            continue

        if (b1 & QOI_MASK_2) == QOI_OP_LUMA:
            b2 = reader.read()
            vg = ((b1 & 0x3F) % 256) - 32
            red = (px_value.red + vg - 8 + ((b2 >> 4) & 0x0F)) % 256
            green = (px_value.green + vg) % 256
            blue = (px_value.blue + vg - 8 + (b2 & 0x0F)) % 256
            px_value.update(bytes((red, green, blue)))
            continue

        if (b1 & QOI_MASK_2) == QOI_OP_RUN:
            run = b1 & 0x3F

    return width, height, channels, colorspace, pixel_data
