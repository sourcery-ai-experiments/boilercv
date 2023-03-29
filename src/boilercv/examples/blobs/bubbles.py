"""Find bubbles as blobs."""

import cv2 as cv

from boilercv import EXAMPLE_CINE, RED
from boilercv.data.dataset import VIDEO, prepare_dataset
from boilercv.examples.blobs import draw_blobs, get_blobs_doh
from boilercv.gui import edit_roi, view_images
from boilercv.images import build_mask_from_polygons, convert_image
from boilercv.models.params import PARAMS
from boilercv.types import ArrInt

SOURCE = PARAMS.paths.examples / EXAMPLE_CINE
ROI = SOURCE.parent / f"{SOURCE.stem}.yaml"
NUM_FRAMES = 10


def main():
    input_images = list(get_images())[:NUM_FRAMES]
    roi = edit_roi(input_images[0], ROI)
    # results_log: list[ArrInt] = []
    # results_dog: list[ArrInt] = []
    results_doh: list[ArrInt] = []
    all_results = [
        # results_log,
        # results_dog,
        results_doh,
    ]
    for input_image in input_images:
        image = build_mask_from_polygons(input_image, [roi])
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
    view_images([input_images, *all_results])


def get_images():
    images = prepare_dataset(SOURCE, num_frames=NUM_FRAMES)[VIDEO]
    return list(images.values)


if __name__ == "__main__":
    main()
