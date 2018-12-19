"""
Regroups tools to process MNIST datasets.
"""
from tqdm import tqdm
from brawn.tools.image import image_compress_half
from numpy import sqrt


def _b2int(file, i):
    """
    Converts bytes to int.
    """
    return int.from_bytes(file.read(i), byteorder='big')


def parse(label, images, max=-1):
    """
    Parses a MNIST idx-formatted dataset.

    Parameters
    ----------
    label : string
        idx Labels filename.
    images : string
        idx Images filename.
    max : int, optional
        Number of images to parse if > 0, else, all pictures are parsed.

    Raises
    ------
    IOError
        if Label or Images files have the wrong file signature, or if they have
        a different amount of pictures.

    Returns
    -------
    dataset : list of dict
        class (int) : Label of the image.

        pixelmap (list of list of int) : image compressed by 2.

        size (int) : length of the picture (images are square)

    """
    label_file = open(label, 'rb')
    images_file = open(images, 'rb')

    if _b2int(label_file, 4) != 2049:
        raise IOError('File ' + label + ' is not a label, or corrupted!')
    if _b2int(images_file, 4) != 2051:
        raise IOError('File ' + images + ' is not images, or corrupted!')

    size = _b2int(images_file, 4)
    if _b2int(label_file, 4) != size:
        raise IOError('Size difference between files!')
    size = max if max >= 0 else size

    dimensions = [_b2int(images_file, 4), _b2int(images_file, 4)]

    dataset = []
    for n in tqdm(range(size), desc='Parsing set'):
        label = _b2int(label_file, 1)
        image = []
        for i in range(dimensions[0]):
                image.append([])
                for j in range(dimensions[1]):
                    image[i].append(_b2int(images_file, 1))
        dataset.append({
            'class': label,
            'pixelmap': image_compress_half(image),
            'size': int(dimensions[0] * dimensions[1] / 4)
        })
    label_file.close()
    images_file.close()

    return dataset


def print(set):
    """Print an MNIST picture in ASCII art using shadow characters."""
    print('Label : ' + str(set['class']))
    image = set['pixelmap']
    dim = set['size']
    for i in range(int(sqrt(dim))):
        line = ''
        for j in range(int(sqrt(dim))):
            pixel = image[i][j]
            line += ('█' if pixel > 192
                     else '▓' if pixel > 128
                     else '▒' if pixel > 64
                     else '░')
        print(line)
