"""Given an MP4, find ROI using `opencv` and find contours."""

import cv2 as cv
import numpy as np
from scipy.spatial import ConvexHull

from boilercv import MARKER_COLOR
from boilercv.examples import capture_images
from boilercv.images import (
    convert_image,
    draw_contours,
    find_contours,
    get_8bit_images,
    mask,
    threshold,
)
from boilercv.models.params import PARAMS
from boilercv.types import ArrIntDef
from boilercv.types.base import Img, NBit_T

WINDOW_NAME = "image"
ESC_KEY = ord("\x1b")


def main():
    images = (
        image[:, :, 0]
        for image in get_8bit_images(
            capture_images(PARAMS.paths.examples / "2022-04-08T16-12-42.mp4")
        )
    )
    roi = get_roi(next(images))
    for image in images:
        masked = mask(image, roi)
        thresholded = threshold(masked)
        contours = find_contours(thresholded)
        image_with_contours = draw_contours(image, contours)
        cv.imshow(WINDOW_NAME, image_with_contours)
        if cv.waitKey(100) == ESC_KEY:
            break


def get_roi(image: Img[NBit_T]) -> ArrIntDef:  # noqa: C901
    """Get the region of interest of an image.

    See: https://docs.opencv.org/4.6.0/db/d5b/tutorial_py_mouse_handling.html
    """

    clicks: list[tuple[int, int]] = []

    image = convert_image(image, cv.COLOR_GRAY2RGB)
    (width, height) = image.shape[:-1]
    click = 0
    default_clicks = [(0, 0), (0, width), (height, width), (height, 0)]
    hull = ConvexHull(default_clicks)
    hull_minimum_vertices = 3
    composite_image = image

    def main() -> ArrIntDef:
        nonlocal clicks
        cv.imshow(WINDOW_NAME, image)
        cv.setMouseCallback(WINDOW_NAME, handle_mouse_events)
        while True and cv.waitKey(100) != ESC_KEY:
            pass
        if len(clicks) < hull_minimum_vertices:
            clicks = default_clicks
        else:
            hull.close()
        return np.array(clicks)[hull.vertices]

    def handle_mouse_events(event: int, x: int, y: int, *_):
        """Handle all mouse events. Form a convex hull from left clicks."""
        nonlocal image, click, hull, composite_image
        if event == cv.EVENT_LBUTTONDOWN:
            click += 1
            clicks.append((x, y))
            image = cv.drawMarker(image, clicks[-1], MARKER_COLOR)
            if click == hull_minimum_vertices:
                hull = ConvexHull(clicks, incremental=True)
                composite_image = draw_hull(hull, image)
            elif click > hull_minimum_vertices:
                hull.add_points([clicks[-1]])
                composite_image = draw_hull(hull, image)
            cv.imshow(WINDOW_NAME, composite_image)

    def draw_hull(hull: ConvexHull, image: Img[NBit_T]) -> Img[NBit_T]:
        """Draw a convex hull on the image."""
        image = image.copy()
        clicks = hull.points.astype(int)
        for simplex in hull.simplices:
            image = cv.line(image, clicks[simplex[0]], clicks[simplex[1]], MARKER_COLOR)
        return image

    return main()


if __name__ == "__main__":
    main()
