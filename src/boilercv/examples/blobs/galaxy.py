"""Find blobs in the galaxy."""

from skimage import data
from skimage.color import rgb2gray

from boilercv import BLUE, GREEN, RED
from boilercv.examples.blobs import (
    draw_blobs,
    get_blobs_dog,
    get_blobs_doh,
    get_blobs_log,
)
from boilercv.gui import compare_images


def main():
    image = data.hubble_deep_field()[0:500, 0:500]
    image_gray = rgb2gray(image)
    blobs_log = get_blobs_log(image_gray)
    blobs_dog = get_blobs_dog(image_gray)
    blobs_doh = get_blobs_doh(image_gray)
    all_blobs = [blobs_log, blobs_dog, blobs_doh]
    colors = [RED, GREEN, BLUE]
    titles = [
        "Laplacian of Gaussian",
        "Difference of Gaussian",
        "Determinant of Hessian",
    ]
    sequence = zip(all_blobs, colors, titles, strict=True)
    results = []
    for blobs, color, _title in sequence:
        result = image.copy()
        for blob in blobs:
            draw_blobs(result, blob, color)
        results.append(result)
    compare_images([image, *results])


if __name__ == "__main__":
    main()
