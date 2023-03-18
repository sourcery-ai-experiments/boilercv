from dataclasses import dataclass
from math import sqrt

from skimage.draw import disk, set_color
from skimage.feature import blob_dog, blob_doh, blob_log


def get_blobs_dog(image):
    blobs = blob_dog(
        image,
        # max_sigma=30,
        # threshold=0.1,
    )
    blobs[:, 2] = blobs[:, 2] * sqrt(2)
    return (Blob(*blob) for blob in blobs)


def get_blobs_log(image):
    blobs = blob_log(
        image,
        max_sigma=30,
        num_sigma=10,
        threshold=0.1,
    )
    blobs[:, 2] = blobs[:, 2] * sqrt(2)
    return (Blob(*blob) for blob in blobs)


def get_blobs_doh(image):
    blobs = blob_doh(
        image,
        # min_sigma=1,
        # max_sigma=30,
        # threshold=0.01,
        # overlap=0.30,
    )
    return (Blob(*blob) for blob in blobs)


@dataclass
class Blob:
    y: int
    x: int
    r: int


def draw_blobs(result, blob, color):
    rr, cc = disk(
        (int(blob.y), int(blob.x)),
        int(blob.r),
    )
    set_color(result, (rr, cc), color)
