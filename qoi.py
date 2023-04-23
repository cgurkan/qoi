import argparse
import sys

from PIL import Image

from decoder import decode_to_img
from encoder import encode_img
from utils import replace_extension


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-opr",
        "--operation",
        type=str,
        default="e",
        help="operation to perform (e)ncode or (d)ecode",
    )
    parser.add_argument(
        "-f",
        "--file-path",
        type=str,
        help="path to image file to be encoded(png) or decoded (qoi)",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--out-path",
        type=str,
        help="path to encoded (qoi) or decoded (png) image file ",
        default="out",
        nargs="?",
        const="out",
    )
    args = parser.parse_args(args=None if sys.argv[1:] else ["--help"])

    if args.operation == "e":
        try:
            img = Image.open(args.file_path)
            print("(E) Input Image File: ", args.file_path)
            print("(E) Image Format: ", img.format)
            print("(E) Width: ", img.width)
            print("(E) Height:", img.height)
            print("(E) Channels:", len(img.getbands()))
            print("(E) ColorSpace:", img.getexif().get("ColorSpace", 0))
        except Exception as exc:
            print(f"Cannot load image : {exc}")
            return

        out_path = replace_extension(args.out_path, "qoi")
        print("(E) Output Image File: ", out_path)
        # out_path = replace_extension(args.file_path, "qoi")
        encode_img(img, out_path)

    if args.operation == "d":
        print("(D) Input Image File: ", args.file_path)
        with open(args.file_path, "rb") as qoi:
            file_bytes = qoi.read()

        # out_path = replace_extension(args.file_path, "png")
        out_path = replace_extension(args.out_path, "png")
        print("(D) Output Image File: ", out_path)
        try:
            decode_to_img(file_bytes, out_path)
        except Exception as exc:
            print(f"Cannot decode image : {exc}")
            return


if __name__ == "__main__":
    main()
