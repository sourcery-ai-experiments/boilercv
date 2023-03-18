"""Given a CINE, find ROI using `pyqtgraph` and find contours."""


from boilercv import PARAMS
from boilercv.examples.contours import IMAGES
from boilercv.gui import edit_roi, preview_images
from boilercv.images import draw_contours, find_contours, mask, threshold
from boilercv.types import ImgSeq8


def main():
    roi = edit_roi(PARAMS.paths.examples_data / "roi.yaml", next(IMAGES))
    result: ImgSeq8 = []
    for input_image in IMAGES:
        image = mask(input_image, roi)
        image = threshold(image)
        contours, _ = find_contours(image)
        result.append(draw_contours(input_image, contours))
    preview_images(result)


if __name__ == "__main__":
    main()
