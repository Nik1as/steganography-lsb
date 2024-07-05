import argparse
import getpass
import hashlib
import io
import random
from typing import List, Tuple

from PIL import Image


def bytes_to_bits(data: bytes) -> List[int]:
    bits = []
    for byte in data:
        bits.extend(int(bit) for bit in format(byte, '08b'))
    return bits


def bits_to_bytes(bits: List[int]) -> bytes:
    if len(bits) % 8 != 0:
        bits += [0] * (8 - len(bits) % 8)

    byte_array = bytearray()
    for i in range(0, len(bits), 8):
        byte_str = ''.join(str(bit) for bit in bits[i:i + 8])
        byte = int(byte_str, 2)
        byte_array.append(byte)
    return bytes(byte_array)


def set_lsb(value: int, bit: int) -> int:
    if bit not in (0, 1):
        raise ValueError('bit must be 0 or 1')

    if bit == 1:
        return value | 1
    else:
        return value & ~1


def get_pixels_order(width: int, height: int) -> List[Tuple[int, int, int]]:
    pixels = [(x, y, z) for y in range(height) for x in range(width) for z in range(3)]
    random.shuffle(pixels)
    return pixels


def embed(args):
    if not args.output.name.endswith('.png'):
        print('The output file must be a png file!')
        return

    image = Image.open(io.BytesIO(args.cover.read()))
    data_bytes = args.data.read()

    length_bits = bytes_to_bits(len(data_bytes).to_bytes(4))
    bits = length_bits + bytes_to_bits(data_bytes)

    if image.width * image.height * 3 < len(bits) + 32:
        print('The image is too small!')
        return

    for (x, y, z), bit in zip(get_pixels_order(image.width, image.height), bits):
        if bit is None:
            break

        pixel = list(image.getpixel((x, y)))
        pixel[z] = set_lsb(pixel[z], bit)
        image.putpixel((x, y), tuple(pixel))

    image.save(args.output, format='png')


def extract(args):
    image = Image.open(io.BytesIO(args.image.read()))
    data_bits = list()

    pixels_iter = iter(get_pixels_order(image.width, image.height))
    for x, y, z in pixels_iter:
        pixel = list(image.getpixel((x, y)))
        bit = pixel[z] & 1
        data_bits.append(bit)

        if len(data_bits) == 32:
            length_bytes = bits_to_bytes(data_bits)
            data_length = int.from_bytes(length_bytes) * 8
            break

    data_bits = list()
    for x, y, z in pixels_iter:
        pixel = list(image.getpixel((x, y)))
        bit = pixel[z] & 1
        data_bits.append(bit)

        if len(data_bits) >= data_length:
            break

    args.output.write(bits_to_bytes(data_bits))


def parse_args():
    parser = argparse.ArgumentParser(description='Save data in the LSB-Bits of an image')
    subparsers = parser.add_subparsers(required=True)

    parser_embed = subparsers.add_parser('embed', help='embed the data in an cover image')
    parser_embed.add_argument('cover', type=argparse.FileType('rb'), help='cover image')
    parser_embed.add_argument('data', type=argparse.FileType('rb'), help='file with the secret data')
    parser_embed.add_argument('output', type=argparse.FileType('wb'), help='output file')
    parser_embed.set_defaults(func=embed)

    parser_extract = subparsers.add_parser('extract', help='extract the data from an image')
    parser_extract.add_argument('image', type=argparse.FileType('rb'), help='image with secret data')
    parser_extract.add_argument('output', type=argparse.FileType('wb'), help='output file')
    parser_extract.set_defaults(func=extract)

    return parser.parse_args()


def main():
    args = parse_args()

    password = getpass.getpass()
    password = hashlib.sha512(password.encode()).hexdigest()
    random.seed(password)

    args.func(args)


if __name__ == '__main__':
    main()
