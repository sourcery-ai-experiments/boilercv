"""Detect the boiling surface."""

from warnings import warn

import cv2 as cv
import numpy as np
import xarray as xr
from scipy.ndimage import (
    center_of_mass,
    generate_binary_structure,
    label,
    labeled_comprehension,
)

from boilercv import DEBUG
from boilercv.captivate.previews import get_calling_scope_name, save_roi, view_images
from boilercv.data import VIDEO, YX_PX, apply_to_img_da
from boilercv.data.frames import df_points
from boilercv.data.sets import get_dataset
from boilercv.examples import EXAMPLE_NUM_FRAMES, EXAMPLE_ROI, EXAMPLE_VIDEO_NAME
from boilercv.images import scale_bool
from boilercv.images.cv import find_contours, get_wall
from boilercv.types import DA, ArrInt, Img


def main():
    ds = get_dataset(EXAMPLE_VIDEO_NAME, EXAMPLE_NUM_FRAMES)
    video = ds[VIDEO]
    roi = ds["roi"]
    wall: DA = apply_to_img_da(get_wall, scale_bool(roi), name="wall")
    boiling_surface, boiling_surface_coords = xr.apply_ufunc(
        find_boiling_surface,
        scale_bool(wall),
        input_core_dims=[YX_PX],
        output_core_dims=[YX_PX, ["test"]],
    )
    contours = find_contours(scale_bool(wall.values), method=cv.CHAIN_APPROX_SIMPLE)
    if len(contours) > 1:
        warn("More than one contour found when searching for the ROI.", stacklevel=1)
    save_roi(contours[0], EXAMPLE_ROI)
    view_images(dict(boiling_surface=boiling_surface, roi=roi))


def find_boiling_surface(img: Img) -> tuple[Img, ArrInt]:
    """Find the boiling surface."""

    # Parameters for finding prominent horizontal lines
    wide_rectangular_ksize = [9, 3]  # Enhance horizontal lines
    threshold = 0.6

    # The range to consider a connected component to be the boiling surface
    (height, width) = img.shape
    min_size_px = 8
    ypx_min = height / 2
    xpx_mid = width / 2
    xpx_max_dist = width / 8
    xpx_min = xpx_mid - xpx_max_dist
    xpx_max = xpx_mid + xpx_max_dist

    # Find prominent horizontal lines
    corners = cv.cornerHarris(src=img, blockSize=2, ksize=3, k=0.04)
    lines = -1 * corners  # Linear features are strongly negative in Harris
    blurred = cv.blur(lines, ksize=wide_rectangular_ksize)
    scaled = (blurred - blurred.min()) / (blurred.max() - blurred.min())
    binarized = scaled > threshold

    # Find connected components and their centers
    # ? cv.connectedComponents and cv.moments could also be used
    # ? Consider re-implementing if slow
    find_diag_conns = generate_binary_structure(rank=2, connectivity=2)
    labeled_img, num_objects = label(input=binarized, structure=find_diag_conns)  # type: ignore
    labels = range(1, num_objects + 1)  # Exclude 0-labeled background
    sizes_px = labeled_comprehension(
        input=binarized,
        labels=labeled_img,
        index=labels,
        func=np.count_nonzero,
        out_dtype=int,
        default=0,
    )
    objs = (
        df_points(
            np.array(center_of_mass(input=binarized, labels=labeled_img, index=labels))
            .round()
            .astype(int)  # Not img dtype. df contains coords, not pixel values
        )
        .assign(**dict(label=labels, size_px=sizes_px))
        .rename(axis="columns", mapper=dict(ypx="ypx_center", xpx="xpx_center"))
        .set_index("label", drop=True)
    )

    # Consider the boiling surface to be the largest object in range
    objs_in_range = objs[
        (objs.size > min_size_px)
        & (objs.ypx_center > ypx_min)
        & (objs.xpx_center > xpx_min)
        & (objs.xpx_center < xpx_max)
    ]
    label_largest_in_range = objs_in_range.size_px.idxmax()
    boiling_surface = labeled_img == label_largest_in_range

    # Get a line segment corresponding to the boiling surface
    points = df_points(np.array(boiling_surface.nonzero()).T)
    xpx_left = points.xpx.min()
    xpx_right = points.xpx.max()
    ypx_horizontal = np.round(points.ypx.mean()).astype(int)
    boiling_surface_coords = np.array(
        [ypx_horizontal, xpx_left, ypx_horizontal, xpx_right]
    ).astype(int)

    if DEBUG:
        view_images(
            name=get_calling_scope_name(),
            images=dict(
                img=img,
                corners=corners,
                lines=lines,
                blurred=blurred,
                scaled=scaled,
                binarized=binarized,
                labeled_img=labeled_img,
                boiling_surface=boiling_surface,
            ),
        )
    return boiling_surface, boiling_surface_coords


if __name__ == "__main__":
    main()
