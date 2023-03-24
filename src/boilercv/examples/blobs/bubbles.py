"""Find bubbles as blobs."""

import cv2 as cv

from boilercv import IMAGES, RED
from boilercv.data import prepare_dataset
from boilercv.examples.blobs import draw_blobs, get_blobs_doh
from boilercv.gui import compare_images, edit_roi
from boilercv.images import convert_image, mask
from boilercv.models.params import PARAMS
from boilercv.types import ImgSeq8

SOURCE = PARAMS.paths.examples / "2022-11-30T13-41-00.cine"
NUM_FRAMES = 10


def main():
    input_images = list(get_images())[:NUM_FRAMES]
    roi = edit_roi(input_images[0], PARAMS.paths.examples / "roi.yaml")
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


def get_images():
    images = prepare_dataset(SOURCE, num_frames=NUM_FRAMES)[IMAGES]
    return list(images.values)


if __name__ == "__main__":
    main()
