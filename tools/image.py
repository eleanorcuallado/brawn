"""
Module regrouping tools to process images.
"""
from brian2 import ms


def image_compress_half(image):
    """Compress a square image in half with the Bilinear algorithm."""
    return [[(image[i][j]
              + image[i+1][j]
              + image[i][j+1]
              + image[i+1][j+1]) / 4
            for j in range(0, len(image), 2)]
            for i in range(0, len(image), 2)]


def image2spikes(pixel_map, spike_time=(0*ms)):
    """
    Converts a picture into a spike train with a threshold of 128.

    Parameters
    ----------
    pixel_map: list of list of int
        Picture pixel map.
    spike_time: `brian2.Quantity`, optional
        Moment at which the picture should spike.

    Returns
    -------
    indices: list of int
        Indices of spiking neurons.
    times: list of `brian2.Quantity`
        Times of spiking neurons.
    """
    indices = []
    times = []
    pix_id = 0
    for line in pixel_map:
        for pixel in line:
            if pixel > 128:
                indices.append(pix_id)
                times.append(spike_time)
            pix_id += 1
    return indices, times
