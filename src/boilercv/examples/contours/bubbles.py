"""Given a CINE, find ROI using `pyqtgraph` and find contours."""


from matplotlib.pyplot import subplot_mosaic

from boilercv import PARAMS
from boilercv.examples.contours import IMAGES
from boilercv.gui import compare_images, edit_roi
from boilercv.images import draw_contours, find_contours, load_roi, mask, threshold
from boilercv.types import ArrIntDef, Img, ImgSeq8, NBit_T

ALL_IMAGES = list(IMAGES)
ROI_FILE = PARAMS.paths.examples_data / "roi.yaml"


def main():
    preview_contours(
        block_size=11, thresh_dist_from_mean=2, contour_index=-1, thickness=2
    )


def preview_contours(
    block_size: int,
    thresh_dist_from_mean: int,
    contour_index: int,
    thickness: int,
    interact: bool = False,
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
    to_preview = [input_images, all_masked, all_thresholded, contoured]
    for image in input_images:
        contours, masked, thresholded = get_contours(
            image, roi, block_size, thresh_dist_from_mean
        )
        all_contours.append(contours)
        all_masked.append(masked)
        all_thresholded.append(thresholded)
        contoured.append(draw_contours(image, contours, contour_index, thickness))
    if interact:
        interact_with_images(*[image[0] for image in to_preview])
    else:
        compare_images(to_preview)
        return all_contours


def get_contours(
    input_image: Img[NBit_T],
    roi: ArrIntDef,
    block_size: int,
    thresh_dist_from_mean: int,
) -> tuple[list[ArrIntDef], Img[NBit_T], Img[NBit_T]]:
    masked = mask(input_image, roi)
    thresholded = threshold(masked, block_size, thresh_dist_from_mean)
    return find_contours(thresholded), masked, thresholded


def interact_with_images(_input_image, _masked, thresholded, contoured):
    _plt, ax = subplot_mosaic(
        [
            [
                # "input",
                # "masked",
                "thresholded",
                "contoured",
            ]
        ]
    )
    for ax_ in ax.values():  # type: ignore
        ax_.axis("off")
    # ax["input"].imshow(input_image, cmap="gray")  # type: ignore
    # ax["masked"].imshow(masked, cmap="gray")  # type: ignore
    ax["thresholded"].imshow(thresholded, cmap="gray")  # type: ignore
    ax["contoured"].imshow(contoured, cmap="gray")  # type: ignore


if __name__ == "__main__":
    main()
