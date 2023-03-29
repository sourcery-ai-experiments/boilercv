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

from boilercv import EXAMPLE_BIG_CINE, EXAMPLE_CINE, EXAMPLE_CINE_ZOOMED
from boilercv.data import PX_DIMS, apply_to_img_da
from boilercv.data.dataset import VIDEO, prepare_dataset
from boilercv.data.frames import df_points, frame_lines
from boilercv.data.models import Dimension
from boilercv.gui import compare_images, save_roi
from boilercv.images import (
    apply_mask,
    binarize,
    build_mask_from_polygons,
    find_contours,
    find_line_segments,
    flood,
    morph,
)
from boilercv.models.params import PARAMS
from boilercv.types import DA, DS, ArrInt, Img

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
        EXAMPLE_BIG_CINE,
        EXAMPLE_BIG_CINE.parent.parent / f"{EXAMPLE_BIG_CINE.stem}.yaml",
        PREVIEW,
    )


def process(source: Path, roi_path: Path, preview: bool = False):
    ds = prepare_dataset(source, NUM_FRAMES)
    video = ds[VIDEO]

    # TODO: Refactor this logic out and see if dims can be reordered
    bin_packed = apply_to_img_da(binarize, video, vectorize=True)
    bin_unpacked = xr_apply_unpackbits(xr_apply_packbits(video), ds)
    compare_images([bin_packed.values, bin_unpacked.values])

    # Get the ROI
    maximum = video.max("frames").rename("maximum")
    flooded_max = apply_to_img_da(flood, video.max("frames"), name="flooded_max")
    flooded_closed, roi, dilated = apply_to_img_da(morph, flooded_max, returns=3)
    flooded_closed = flooded_closed.rename("flooded_closed")
    roi = roi.rename("roi")
    dilated = dilated.rename("dilated")
    boundary_roi = xr.apply_ufunc(
        lambda img1, img2: img1 ^ img2,
        roi,
        dilated,
        input_core_dims=[PX_DIMS] * 2,
        output_core_dims=[PX_DIMS],
    ).rename("boundary_roi")

    _packed_flooded_closed = xr_apply_packbits(flooded_closed)

    # Mask the first image
    first_image = video.isel(frames=0)
    first_image_roi_only = apply_to_img_da(
        apply_mask, first_image, kwargs=dict(mask=roi.values)
    )

    # Find the boiling surface
    boiling_surface, _boiling_surface_coords = xr.apply_ufunc(
        find_boiling_surface,
        flooded_closed,
        input_core_dims=[PX_DIMS],
        output_core_dims=[PX_DIMS, ["test"]],
    )

    # Save and reconstruct the ROI
    contours = find_contours(roi.values, method=cv.CHAIN_APPROX_SIMPLE)
    roi_poly_ = contours.pop()
    _roi_poly = df_points(roi_poly_)
    if contours:
        warn("More than one contour found when searching for the ROI.")
    save_roi(roi_poly_, roi_path)

    if preview:
        binarized_first = binarize(first_image.values)
        roi2 = build_mask_from_polygons(binarized_first, [roi_poly_])
        roi_diff = roi.values ^ roi2
        compare_images(
            dict(
                # Get the ROI
                maximum=maximum.values,
                flooded_max=flooded_max.values,
                # Get the boiling surface
                boiling_surface=boiling_surface.values,
                roi=roi,
                dilated_roi=dilated.values,
                boundary_roi=boundary_roi.values,
                # Mask the first image
                first_image=first_image,
                first_image_roi_only=first_image_roi_only.values,
                # Find the surface
                # Save and reconstruct the ROI
                roi_diff=roi_diff,
            )
        )


def xr_apply_packbits(da: DA):
    """Pack the bits of the first image dimension of a data array."""
    first_image_dim = 1 if "frames" in da.dims else 0
    return xr.apply_ufunc(
        np.packbits,
        da,
        input_core_dims=[PX_DIMS],
        output_core_dims=[PX_DIMS],
        exclude_dims={PX_DIMS[0]},
        kwargs=dict(axis=first_image_dim),
    ).rename(f"{da.name}_packed")


def xr_apply_unpackbits(da: DA, ds: DS):
    """Unpack the bits of the first image dimension of a data array."""
    first_image_dim = 1 if "frames" in da.dims else 0
    ypx = Dimension(
        dim=PX_DIMS[0],
        long_name="Height",
        units="px",
    )
    da = (
        xr.apply_ufunc(
            lambda img: np.unpackbits(img, axis=first_image_dim).astype(bool),
            da,
            input_core_dims=[PX_DIMS],
            output_core_dims=[PX_DIMS],
            exclude_dims={PX_DIMS[0]},
        )
        .rename(str(da.name).removesuffix("_packed"))
        .assign_coords(**ds[PX_DIMS])
    )
    da = ypx.assign_to(da)
    return da


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
        compare_images(
            dict(
                img=img,
                corners=corners,
                lines=lines,
                blurred=blurred,
                scaled=scaled,
                binarized=binarized,
                labeled_img=labeled_img,
                boiling_surface=boiling_surface,
            )
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
