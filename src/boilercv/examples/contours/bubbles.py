"""Given a CINE, find ROI using `pyqtgraph` and find contours."""


from matplotlib.pyplot import imshow

from boilercv import PARAMS
from boilercv.examples.contours import IMAGES
from boilercv.gui import edit_roi, preview_images
from boilercv.images import draw_contours, find_contours, load_roi, mask, threshold
from boilercv.types import ImgSeq8

images = list(IMAGES)


def main(interact=False, thickness: int = 2):
    input_images = [images[0]] if interact else images
    if interact:
        roi = load_roi(PARAMS.paths.examples_data / "roi.yaml", input_images[0])
    else:
        roi = edit_roi(PARAMS.paths.examples_data / "roi.yaml", input_images[0])
    result: ImgSeq8 = []
    for input_image in input_images:
        image = mask(input_image, roi)
        image = threshold(image)
        contours, _ = find_contours(image)
        result.append(draw_contours(input_image, contours, thickness))
    if interact:
        imshow(result[0])
    else:
        preview_images(result)


if __name__ == "__main__":
    main()
