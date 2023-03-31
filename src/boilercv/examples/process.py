"""Prepare the video for saving to disk.

Computing the median is a costly operation, so don't do it if we don't have to. Padding
with OpenCV is faster than numpy padding.
"""

from pathlib import Path
from warnings import warn

import cv2 as cv
import numpy as np
import pandas as pd
import xarray as xr
from scipy.ndimage import (
    center_of_mass,
    generate_binary_structure,
    label,
    labeled_comprehension,
)

from boilercv import EXAMPLE_CINE, EXAMPLE_CINE_ZOOMED, EXAMPLE_FULL_CINE
from boilercv.data import YX_PX, apply_to_img_da
from boilercv.data.frames import df_points, frame_lines
from boilercv.data.packing import pack, unpack
from boilercv.data.video import VIDEO, prepare_dataset
from boilercv.gui import get_calling_scope_name, save_roi, view_images
from boilercv.images import scale_bool
from boilercv.images.cv import (
    apply_mask,
    binarize,
    build_mask_from_polygons,
    find_contours,
    find_line_segments,
    flood,
    morph,
)
from boilercv.models.params import PARAMS
from boilercv.types import DA, DF, ArrInt, Img, Vid

PREVIEW = True
NUM_FRAMES = 100
DRAWN_CONTOUR_THICKNESS = 2


def main():
    process(
        PARAMS.paths.examples / EXAMPLE_CINE,
        PARAMS.paths.examples / f"{EXAMPLE_CINE.stem}.yaml",
        PREVIEW,
    )
    process(
        PARAMS.paths.examples / EXAMPLE_CINE_ZOOMED,
        PARAMS.paths.examples / f"{EXAMPLE_CINE_ZOOMED.stem}.yaml",
        PREVIEW,
    )
    process(
        EXAMPLE_FULL_CINE,
        EXAMPLE_FULL_CINE.parent.parent / f"{EXAMPLE_FULL_CINE.stem}.yaml",
        PREVIEW,
    )


def process(source: Path, roi_path: Path, preview: bool = False):
    # Prepare the dataset
    ds = prepare_dataset(source, NUM_FRAMES)
    video = ds[VIDEO]

    # Get the ROI
    maximum = video.max("frame").rename("maximum")
    flooded_max: DA = apply_to_img_da(flood, video.max("frame"), name="flooded_max")
    result: tuple[DA, ...] = apply_to_img_da(
        morph, flooded_max, returns=3, name=["flooded_closed", "roi", "dilated"]
    )
    flooded_closed, roi, dilated = result
    boundary_roi = roi ^ dilated

    # Mask the first image
    first_image = video.isel(frame=0)
    first_image_roi_only = apply_to_img_da(
        apply_mask, first_image, roi, name="first_image_roi_only"
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

    masked_images = apply_to_img_da(
        apply_mask, video, roi, vectorize=True, name="masked_images"
    )

    binarized_images = apply_to_img_da(
        binarize, masked_images, vectorize=True, name="binarized_images"
    )

    df = get_all_contours(masked_images.values, method=cv.CHAIN_APPROX_SIMPLE)

    # Save and reconstruct the ROI
    # TODO
    contours = find_contours(flooded_closed.values, method=cv.CHAIN_APPROX_SIMPLE)
    roi_poly_ = contours.pop()
    _roi_poly = df_points(roi_poly_)
    if contours:
        warn("More than one contour found when searching for the ROI.")
    save_roi(roi_poly_, roi_path)

    # TODO: Refactor this logic out and see if dims can be reordered
    binar = apply_to_img_da(binarize, video, vectorize=True)
    binar_unpacked = unpack(pack(binar))
    rgba = binar.values[0:4, :, :]
    view_images([binar, binar_unpacked])

    if preview:
        binarized_first = binarize(first_image.values)
        roi2 = build_mask_from_polygons(scale_bool(binarized_first), [roi_poly_])
        roi_diff = roi.values ^ roi2
        view_images(
            dict(
                # Get the ROI
                maximum=maximum,
                flooded_max=flooded_max,
                # Get the boiling surface
                boiling_surface=boiling_surface,
                roi=roi,
                boundary_roi=boundary_roi,
                # Mask the first image
                first_image=first_image,
                first_image_roi_only=first_image_roi_only,
                # Save and reconstruct the ROI
                roi_diff=roi_diff,
            )
        )


def get_all_contours(video: Vid, method: int = cv.CHAIN_APPROX_NONE) -> DF:
    """Get all contours."""
    all_contours: list[DF] = []
    contours_index = ["contour", "point"]
    index = ["frame", *contours_index]
    for image in ~video:
        contours = pd.concat(
            axis="index",
            names=["contour", "point"],
            objs={
                contour_num: df_points(
                    contour
                )  # TODO: See if this can be done outside. 60% of the time is spent here.
                # TODO: Compare binarized to non-binarized contour results. Binarized
                # TODO: might be producing a lot more?
                for contour_num, contour in enumerate(find_contours(image, method))
            },
        )
        all_contours.append(contours)
    return pd.concat(
        axis="index",
        names=["frame", "contour", "point"],
        objs=dict(enumerate(all_contours)),
    )


# TODO: Is this faster?


def get_all_contours2(video: Vid, method: int = cv.CHAIN_APPROX_NONE):
    """Get all contours."""
    all_contours: list[DF] = []
    contours_index = ["contour", "point"]
    index = ["frame", *contours_index]
    for image in ~video:
        contours = pd.concat(
            axis="index",
            names=["contour", "point"],
            objs={
                contour_num: pd.DataFrame(contour)
                for contour_num, contour in enumerate(find_contours(image, method))
            },
        )
        all_contours.append(contours)
    return pd.concat(
        axis="index",
        names=["frame", "contour", "point"],
        objs=dict(enumerate(all_contours)),
    )


def later(all_contours):
    with pd.HDFStore("store.h5", "w") as store:
        for frame, contours in enumerate(all_contours):
            for j, contour in enumerate(contours):
                contour.to_hdf(store, f"c_{frame}_{j}")

    all_contours2 = []
    with pd.HDFStore("store.h5", "r") as store:
        all_contours2.extend(
            [pd.read_hdf(store, f"c_{frame}_{j}") for j, _ in enumerate(contours)]
            for frame, contours in enumerate(all_contours)
        )

    for contours, contours2 in zip(all_contours, all_contours2, strict=True):
        for contour, contour2 in zip(contours, contours2, strict=True):
            assert contour.equals(contour2)


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


def get_lines2(image):
    """Get line segments in an image."""
    lines_, lsd = find_line_segments(image)
    lined = lsd.drawSegments(image, lines_)
    lines = frame_lines(lines_)
    midpoints = df_points([lines.ypx.T.mean(), lines.xpx.T.mean()])
    distances = df_points([lines.ypx[1] - lines.ypx[0], lines.xpx[1] - lines.xpx[0]])
    lengths = distances.T.pow(2).sum().pow(1 / 2).rename("px")
    angles = pd.Series(np.arctan2(distances.ypx, distances.xpx)).rename("deg")
    lines = (
        pd.concat(
            axis="columns",
            keys=["line", "midpoint", "length", "angle"],
            objs=[
                lines.set_axis(axis="columns", labels=["ypx0", "xpx0", "ypx1", "xpx1"]),
                midpoints,
                lengths,
                angles,
            ],
        )
        .rename_axis(axis="index", mapper="line")
        .rename_axis(axis="columns", mapper=["metric", "dim"])
    )
    return lined, lines


if __name__ == "__main__":
    main()
