"""Given an MP4, find ROI using `opencv` and find contours."""

import cv2 as cv
import numpy as np
from scipy.spatial import ConvexHull

from boilercv import MARKER_COLOR
from boilercv.examples import get_first_channel, gray_to_rgb, video_images
from boilercv.examples.contours import ESC_KEY, mask_and_threshold
from boilercv.models.params import Params
from boilercv.types import ArrIntDef, Img, Img8, NBit_T

WINDOW_NAME = "image"


def main(params: Params):
    with video_images(
        params.paths.examples_data / "results_2022-04-08T16-12-42.mp4"
    ) as images:
        image: Img8 = get_first_channel(next(images))
        roi = get_roi(image)
        for image in images:
            image = get_first_channel(next(images))
            thresholded = mask_and_threshold(image, roi)
            contours, _ = cv.findContours(
                image=~thresholded,
                mode=cv.RETR_EXTERNAL,
                method=cv.CHAIN_APPROX_SIMPLE,
            )
            # Need three-channel image to paint colored contours
            three_channel_gray = gray_to_rgb(image)
            # ! Careful: cv.drawContours modifies in-place AND returns
            image_with_contours = cv.drawContours(
                image=three_channel_gray,
                contours=contours,
                contourIdx=-1,
                color=(0, 255, 0),
                thickness=3,
            )
            cv.imshow(WINDOW_NAME, image_with_contours)
            if cv.waitKey(100) == ESC_KEY:
                break


def get_roi(image: Img[NBit_T]) -> ArrIntDef:
    """Get the region of interest of an image.

    See: https://docs.opencv.org/4.6.0/db/d5b/tutorial_py_mouse_handling.html
    """

    clicks: list[tuple[int, int]] = []

    image = gray_to_rgb(image)
    click = 0
    hull = ConvexHull([(0, 0), (0, 1), (1, 0)])
    composite_image = image

    def main() -> ArrIntDef:
        cv.imshow(WINDOW_NAME, image)
        cv.setMouseCallback(WINDOW_NAME, handle_mouse_events)
        while True and cv.waitKey(10) != ESC_KEY:
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
    try:
        main(Params.get_params())
    finally:
        cv.destroyAllWindows()
