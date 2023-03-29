"""Given a CINE, find ROI using `pyqtgraph` and find contours."""

from collections.abc import Sequence

from matplotlib.pyplot import subplot_mosaic

from boilercv import EXAMPLE_CINE
from boilercv.data.dataset import VIDEO, prepare_dataset
from boilercv.gui import edit_roi, load_roi, view_images
from boilercv.images import (
    binarize,
    build_mask_from_polygons,
    draw_contours,
    find_contours,
    scale_bool,
)
from boilercv.models.params import PARAMS
from boilercv.types import ArrInt, Img, ImgBool

# TODO: Make a separate `bubbles_auto.py` example

SOURCE = PARAMS.paths.examples / EXAMPLE_CINE
NUM_FRAMES = 300
ROI_FILE = PARAMS.paths.examples / "roi_auto.yaml"


def main():
    images = get_images()
    preview_contours(
        images=images,
        block_size=11,
        thresh_dist_from_mean=2,
        contour_index=-1,
        thickness=2,
    )


def preview_contours(
    images: Sequence[Img],
    block_size: int,
    thresh_dist_from_mean: int,
    contour_index: int,
    thickness: int,
    interact: bool = False,
) -> list[list[ArrInt]] | None:
    input_images = [images[0]] if interact else images
    if interact:
        roi = load_roi(input_images[0], ROI_FILE)
    else:
        roi = edit_roi(input_images[0], ROI_FILE)
    all_contours: list[list[ArrInt]] = []
    all_masked: list[Img] = []
    all_thresholded: list[ImgBool] = []
    contoured: list[Img] = []
    to_preview = dict(
        input_images=input_images,
        all_masked=all_masked,
        all_thresholded=all_thresholded,
        contoured=contoured,
    )
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
        view_images(to_preview)
        return all_contours


def get_images():
    images = prepare_dataset(SOURCE, num_frames=NUM_FRAMES)[VIDEO]
    return list(images.values)


def get_contours(
    input_image: ArrInt,
    roi: ArrInt,
    block_size: int,
    thresh_dist_from_mean: int,
) -> tuple[list[ArrInt], ArrInt, ImgBool]:
    masked = build_mask_from_polygons(input_image, [roi])
    thresholded = binarize(masked, block_size, thresh_dist_from_mean)
    return find_contours(scale_bool(thresholded)), masked, thresholded


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
