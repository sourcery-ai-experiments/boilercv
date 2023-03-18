"""Given a CINE, find ROI using `pyqtgraph` and find contours."""


from matplotlib.pyplot import subplot_mosaic

from boilercv import PARAMS
from boilercv.examples.contours import IMAGES
from boilercv.gui import compare_images, edit_roi
from boilercv.images import draw_contours, find_contours, load_roi, mask, threshold
from boilercv.types import ArrIntDef, Img, ImgSeq8, NBit_T

ALL_IMAGES = list(IMAGES)
ROI_FILE = PARAMS.paths.examples_data / "roi.yaml"


def preview_contours(
    interact: bool = False, thickness: int = 2
) -> list[list[ArrIntDef]] | None:
    input_images = [ALL_IMAGES[0]] if interact else ALL_IMAGES
    if interact:
        roi = load_roi(ROI_FILE, input_images[0])
    else:
        roi = edit_roi(ROI_FILE, input_images[0])
    all_contours: list[list[ArrIntDef]] = []
    all_masked: ImgSeq8 = []
    all_thresholded: ImgSeq8 = []
    contoured: ImgSeq8 = []
    for image in input_images:
        contours, masked, thresholded = get_contours(image, roi)
        all_contours.append(contours)
        all_masked.append(masked)
        all_thresholded.append(thresholded)
        contoured.append(draw_contours(image, contours, thickness))
    if interact:
        _, ax = subplot_mosaic([["input", "masked"], ["thresholded", "contoured"]])
        ax["input"].imshow(input_images[0], cmap="gray")  # type: ignore
        ax["masked"].imshow(all_masked[0], cmap="gray")  # type: ignore
        ax["thresholded"].imshow(all_thresholded[0], cmap="gray")  # type: ignore
        ax["contoured"].imshow(contoured[0], cmap="gray")  # type: ignore
    else:
        compare_images([input_images, all_masked, all_thresholded, contoured])
        return all_contours


def get_contours(
    input_image: Img[NBit_T], roi
) -> tuple[list[ArrIntDef], Img[NBit_T], Img[NBit_T]]:
    masked = mask(input_image, roi)
    thresholded = threshold(masked)
    return find_contours(thresholded), masked, thresholded


if __name__ == "__main__":
    all_contours = preview_contours()
