# LSB Image Steganography

This tool embeds data in an image. It utilizes the least significant bit (LSB) technique to encode hidden information into the pixel values of the cover image. The utilized pixels are selected randomly with a pseudorandom number generator (PRNG), which is initialized with a user-provided password.

## Installation

``pip install -r requirements.txt``

## Usage

```
usage: stego-lsb.py [-h] {embed,extract} ...

Save data in the LSB-Bits of an image

positional arguments:
  {embed,extract}
    embed          embed the data in an cover image
    extract        extract the data from an image

options:
  -h, --help       show this help message and exit
```

```
usage: stego-lsb.py embed [-h] cover data output

positional arguments:
  cover       cover image
  data        file with the secret data
  output      output file

options:
  -h, --help  show this help message and exit
```

```
usage: stego-lsb.py extract [-h] image output

positional arguments:
  image       image with secret data
  output      output file

options:
  -h, --help  show this help message and exit
```

**Example:**

``python3 stego-lsb.py embed cover.png secret.txt secret.png``

``python3 stego-lsb.py extract secret.png extracted.txt``