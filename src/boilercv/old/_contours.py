"""Given a CINE, find ROI using `pyqtgraph` and find contours."""

from matplotlib.pyplot import subplot_mosaic

from boilercv.captivate.previews import edit_roi, load_roi, view_images
from boilercv.examples import EXAMPLE_FRAME_LIST, EXAMPLE_ROI
from boilercv.images import scale_bool
from boilercv.images.cv import (
    apply_mask,
    binarize,
    build_mask_from_polygons,
    draw_contours,
    find_contours,
)
from boilercv.types import ArrInt, Img, ImgBool


def main():
    preview_contours(
        block_size=11,
        thresh_dist_from_mean=2,
        contour_index=-1,
        thickness=2,
    )


def preview_contours(
    block_size: int,
    thresh_dist_from_mean: int,
    contour_index: int,
    thickness: int,
    interact: bool = False,
) -> list[list[ArrInt]] | None:
    input_images = [EXAMPLE_FRAME_LIST[0]] if interact else EXAMPLE_FRAME_LIST
    if interact:
        roi = load_roi(input_images[0], EXAMPLE_ROI)
    else:
        roi = edit_roi(input_images[0], EXAMPLE_ROI)
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
        contours, masked, thresholded = _get_contours(
            image, roi, block_size, thresh_dist_from_mean
        )
        all_contours.append(contours)
        all_masked.append(masked)
        all_thresholded.append(thresholded)
        contoured.append(draw_contours(image, contours, contour_index, thickness))
    if interact:
        interact_with_images(*[image[0] for image in to_preview.values()])
    else:
        view_images(to_preview)
        return all_contours


def _get_contours(
    input_image: ArrInt,
    roi: ArrInt,
    block_size: int,
    thresh_dist_from_mean: int,
) -> tuple[list[ArrInt], ArrInt, ImgBool]:
    masked = apply_mask(input_image, build_mask_from_polygons(input_image, [roi]))
    thresholded = binarize(masked, block_size, thresh_dist_from_mean)
    return find_contours(scale_bool(~thresholded)), masked, thresholded


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
    for ax_ in ax.values():
        ax_.axis("off")
    # ax["input"].imshow(input_image, cmap="gray")
    # ax["masked"].imshow(masked, cmap="gray")
    ax["thresholded"].imshow(thresholded, cmap="gray")  # type: ignore
    ax["contoured"].imshow(contoured, cmap="gray")  # type: ignore


if __name__ == "__main__":
    main()
