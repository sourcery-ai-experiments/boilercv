"""Find bubbles as blobs.."""

import cv2 as cv

from boilercv import PARAMS, RED, convert_image
from boilercv.examples.blobs import draw_blobs, get_blobs_doh
from boilercv.examples.contours import IMAGES
from boilercv.gui import compare_images, edit_roi
from boilercv.images import mask
from boilercv.types import ImgSeq8

NUM_FRAMES = 10


def main():
    input_images = list(IMAGES)[:NUM_FRAMES]
    roi = edit_roi(PARAMS.paths.examples_data / "roi.yaml", input_images[0])
    # results_log: ImgSeq8 = []
    # results_dog: ImgSeq8 = []
    results_doh: ImgSeq8 = []
    all_results = [
        # results_log,
        # results_dog,
        results_doh,
    ]
    for input_image in input_images:
        image = mask(input_image, roi)
        image = ~image
        all_blobs = [
            # get_blobs_log(image),
            # get_blobs_dog(image),
            get_blobs_doh(image),
        ]
        sequence = zip(all_blobs, all_results, strict=True)
        for blobs, results in sequence:
            result = convert_image(input_image, cv.COLOR_GRAY2RGB)
            for blob in blobs:
                draw_blobs(result, blob, RED)
            results.append(result)
    compare_images([input_images, *all_results])


if __name__ == "__main__":
    main()
