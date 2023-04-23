import sys

from PIL import Image

import constants as const
from utils import ByteWriter, Pixel


def qoiWrite32(value: int, writer: ByteWriter) -> None:
    writer.write((0xFF000000 & value) >> 24)
    writer.write((0x00FF0000 & value) >> 16)
    writer.write((0x0000FF00 & value) >> 8)
    writer.write((0x000000FF & value))


# The byte stream's end is marked with 7 0x00 bytes followed by a single 0x01 byte.
def write_end(writer: ByteWriter) -> None:
    writer.bytes.extend(const.QOI_PADDING)


def encode(
    img_bytes: bytes, width: int, height: int, channels: int, colorspace: int
):
    total_size = height * width
    pixel_data = (
        img_bytes[i : i + channels] for i in range(0, len(img_bytes), channels)
    )
    max_size = (
        const.QOI_HEADER_SIZE
        + total_size * (channels + 1)
        + sys.getsizeof(const.QOI_PADDING)
    )
    writer = ByteWriter(max_size)
    hash_array = [Pixel() for _ in range(64)]

    # write header
    qoiWrite32(const.QOI_MAGIC, writer)
    qoiWrite32(width, writer)
    qoiWrite32(height, writer)
    writer.write(channels)
    writer.write(colorspace)

    # encode pixels
    run = 0
    prev_px_value = Pixel()
    px_value = Pixel()
    for i, px in enumerate(pixel_data):
        prev_px_value.update(px_value.bytes)
        px_value.update(px)

        if px_value == prev_px_value:
            run += 1
            if run == 62 or (i + 1) >= total_size:
                writer.write(const.QOI_OP_RUN | (run - 1))
                run = 0
            continue

        if run:
            writer.write(const.QOI_OP_RUN | (run - 1))
            run = 0

        index_pos = px_value.hash
        if hash_array[index_pos] == px_value:
            writer.write(const.QOI_OP_INDEX | index_pos)
            continue

        hash_array[index_pos].update(px_value.bytes)

        if px_value.alpha != prev_px_value.alpha:
            writer.write(const.QOI_OP_RGBA)
            writer.write(px_value.red)
            writer.write(px_value.green)
            writer.write(px_value.blue)
            writer.write(px_value.alpha)
            continue

        vr = px_value.red - prev_px_value.red
        vg = px_value.green - prev_px_value.green
        vb = px_value.blue - prev_px_value.blue

        vg_r = vr - vg
        vg_b = vb - vg

        if all(-3 < x < 2 for x in (vr, vg, vb)):
            writer.write(
                const.QOI_OP_DIFF | (vr + 2) << 4 | (vg + 2) << 2 | (vb + 2)
            )
            continue

        elif all(-9 < x < 8 for x in (vg_r, vg_b)) and -33 < vg < 32:
            writer.write(const.QOI_OP_LUMA | (vg + 32))
            writer.write((vg_r + 8) << 4 | (vg_b + 8))
            continue

        writer.write(const.QOI_OP_RGB)
        writer.write(px_value.red)
        writer.write(px_value.green)
        writer.write(px_value.blue)

    write_end(writer)
    return writer.output()


def encode_img(img: Image.Image, out_path: str) -> None:
    """
    Encode an image to a qoi file.
    :param img: The image to encode.
    :param out_path: The path to the output file.
    """
    # Get image size
    width, height = img.size

    # Check if image is too large
    if height >= const.QOI_PIXELS_MAX / width:
        raise ValueError(
            f"Maximum pixels size reached. Cannor larger than {const.QOI_PIXELS_MAX}. Height ({height})xWidth ({width}. )."
        )

    # Check if image has alpha channel
    channels = len(img.getbands())
    if channels not in (const.CHANNELS_RGB, const.CHANNELS_RGBA):
        raise ValueError(
            f"channels must be CHANNELS_RGB ({const.CHANNELS_RGB}) or CHANNELS_RGBA ({const.CHANNELS_RGBA})."
        )

    colorspace = img.getexif().get("ColorSpace", 0)

    if colorspace not in (const.QOI_SRGB, const.QOI_LINEAR):
        raise ValueError(
            f"colorspace must be COLORSPACE_SRGB_WITH_LINEAR_ALPHA ({const.QOI_SRGB}) or COLORSPACE_ALL_CHANNELS_LINEAR ({const.QOI_LINEAR})."
        )

    # Convert image to bytes
    img_bytes = img.tobytes()
    # Encode image
    output = encode(img_bytes, width, height, channels, colorspace)

    # Write output to file
    with open(out_path, "wb") as qoi:
        qoi.write(output)
