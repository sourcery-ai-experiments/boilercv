"""Example of automated boiling surface detection."""


import cv2 as cv
import numpy as np
import xarray as xr
from scipy.ndimage import (
    center_of_mass,
    generate_binary_structure,
    label,
    labeled_comprehension,
)

from boilercv.data import YX_PX, apply_to_img_da
from boilercv.data.frames import df_points
from boilercv.examples import EXAMPLE_VIDEO
from boilercv.gui import get_calling_scope_name, view_images
from boilercv.images import scale_bool
from boilercv.images.cv import apply_mask, flood, morph
from boilercv.types import DA, ArrInt, Img

PREVIEW = True
DRAWN_CONTOUR_THICKNESS = 2


def main():
    # Get the ROI
    flooded_max: DA = apply_to_img_da(
        flood, EXAMPLE_VIDEO.max("frame"), name="flooded_max"
    )
    result: tuple[DA, ...] = apply_to_img_da(
        morph,
        scale_bool(flooded_max),
        returns=3,
        name=["flooded_closed", "roi", "dilated"],
    )
    flooded_closed, roi, dilated = result
    boundary_roi = roi ^ dilated

    # Mask the first image
    first_image = EXAMPLE_VIDEO.isel(frame=0)
    first_image_roi_only = apply_to_img_da(
        apply_mask, first_image, scale_bool(roi), name="first_image_roi_only"
    )
    # Find the boiling surface
    boiling_surface, boiling_surface_coords = xr.apply_ufunc(
        find_boiling_surface,
        scale_bool(flooded_closed),
        input_core_dims=[YX_PX],
        output_core_dims=[YX_PX, ["test"]],
        kwargs=dict(preview=True),
    )
    boiling_surface = boiling_surface.rename("boiling_surface")
    boiling_surface_coords = boiling_surface_coords.rename("boiling_surface_coords")


def find_boiling_surface(img: Img, preview: bool = False) -> tuple[Img, ArrInt]:
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
    labeled_img, num_objects = label(input=binarized, structure=find_diag_conns)
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

    if preview:
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
