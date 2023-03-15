"""Custom ROI and contour finding in MP4 boiling video data."""

import cv2 as cv
import numpy as np
from scipy.spatial import ConvexHull

from boilercv import ESC_KEY, MARKER_COLOR, WHITE
from boilercv.examples import get_first_channel, gray_to_rgb, video_images
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
            frame_with_contours = cv.drawContours(
                image=three_channel_gray,
                contours=contours,
                contourIdx=-1,
                color=(0, 255, 0),
                thickness=3,
            )
            cv.imshow(WINDOW_NAME, frame_with_contours)
            if cv.waitKey(100) == ESC_KEY:
                break


def mask_and_threshold(image: Img[NBit_T], roi: ArrIntDef) -> Img[NBit_T]:
    blank = np.zeros_like(image)
    mask: Img[NBit_T] = ~cv.fillConvexPoly(blank, roi, WHITE)
    masked = cv.add(image, mask)
    return cv.adaptiveThreshold(
        src=masked,
        maxValue=np.iinfo(masked.dtype).max,
        adaptiveMethod=cv.ADAPTIVE_THRESH_MEAN_C,
        thresholdType=cv.THRESH_BINARY,
        blockSize=11,
        C=2,
    )  # type: ignore


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

    def draw_hull(hull: ConvexHull, img: Img[NBit_T]) -> Img[NBit_T]:
        """Draw a convex hull on the image."""
        img = img.copy()
        clicks = hull.points.astype(int)
        for simplex in hull.simplices:
            img = cv.line(img, clicks[simplex[0]], clicks[simplex[1]], MARKER_COLOR)
        return img

    return main()


if __name__ == "__main__":
    try:
        main(Params.get_params())
    finally:
        cv.destroyAllWindows()
