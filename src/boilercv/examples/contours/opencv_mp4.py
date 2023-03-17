"""Given an MP4, find ROI using `opencv` and find contours."""

import cv2 as cv
import numpy as np
from scipy.spatial import ConvexHull

from boilercv import MARKER_COLOR, PARAMS, convert_image, get_8bit_images
from boilercv.examples import capture_images
from boilercv.examples.contours import draw_contours, find_contours, mask, threshold
from boilercv.types import ArrIntDef, Img, NBit_T

WINDOW_NAME = "image"
ESC_KEY = ord("\x1b")


def main():
    images = (
        image[:, :, 0]
        for image in get_8bit_images(
            capture_images(
                PARAMS.paths.examples_data / "results_2022-04-08T16-12-42.mp4"
            )
        )
    )
    roi = get_roi(next(images))
    for image in images:
        masked = mask(image, roi)
        thresholded = threshold(masked)
        contours, _ = find_contours(thresholded)
        image_with_contours = draw_contours(image, contours)
        cv.imshow(WINDOW_NAME, image_with_contours)
        if cv.waitKey(100) == ESC_KEY:
            break


def get_roi(image: Img[NBit_T]) -> ArrIntDef:
    """Get the region of interest of an image.

    See: https://docs.opencv.org/4.6.0/db/d5b/tutorial_py_mouse_handling.html
    """

    clicks: list[tuple[int, int]] = []

    image = convert_image(image, cv.COLOR_GRAY2RGB)
    click = 0
    hull = ConvexHull([(0, 0), (0, 1), (1, 0)])
    composite_image = image

    def main() -> ArrIntDef:
        cv.imshow(WINDOW_NAME, image)
        cv.setMouseCallback(WINDOW_NAME, handle_mouse_events)
        while True and cv.waitKey(100) != ESC_KEY:
            pass
        hull.close()
        return np.array(clicks)[hull.vertices]

    def handle_mouse_events(event: int, x: int, y: int, *_):
        """Handle all mouse events. Form a convex hull from left clicks."""
        nonlocal image, click, hull, composite_image
        if event == cv.EVENT_LBUTTONDOWN:
            click += 1
            clicks.append((x, y))
            image = cv.drawMarker(image, clicks[-1], MARKER_COLOR)
            hull_minimum_vertices = 3
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
