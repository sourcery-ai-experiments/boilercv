"""Given a CINE, find ROI using `pyqtgraph` and find contours."""


from boilercv import (
    PARAMS,
    get_8bit_images,
)
from boilercv.gui import edit_roi, get_video_images, preview_images
from boilercv.images import draw_contours, find_contours, mask, threshold
from boilercv.types import ImgSeq8


def main():
    images = get_8bit_images(
        get_video_images(
            PARAMS.paths.examples_data / "results_2022-11-30T12-39-07_98C.cine"
        )
    )
    roi = edit_roi(PARAMS.paths.examples_data / "roi.yaml", next(images))
    result: ImgSeq8 = []
    for image in images:
        masked = mask(image, roi)
        thresholded = threshold(masked)
        contours, _ = find_contours(thresholded)
        result.append(draw_contours(image, contours))
    preview_images(result)


if __name__ == "__main__":
    main()
