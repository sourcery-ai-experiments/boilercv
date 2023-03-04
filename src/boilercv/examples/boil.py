import cv2 as cv
import numpy as np
import numpy.typing as npt
from scipy.spatial import ConvexHull

from boilercv.common import ESC_KEY, MARKER_COLOR, WHITE
from boilercv.models.params import Params
from boilercv.types import Img, Img8Bit, NBit_T

WINDOW_NAME = "image"


def main(params: Params):
    cap = cv.VideoCapture(
        str(params.paths.examples_mp4 / "results_2022-04-08T16-12-42.mp4")
    )
    frame: Img8Bit = get_frame(cap)
    blank = np.zeros_like(frame)
    roi = get_roi(frame)
    while cap.isOpened():
        frame = get_frame(cap)
        mask = ~cv.fillConvexPoly(blank, roi, WHITE)
        masked = cv.add(frame, mask)
        gray = cv.cvtColor(masked, cv.COLOR_BGR2GRAY)
        binarized = cv.adaptiveThreshold(
            gray, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2
        )
        contours, _hierarchy = cv.findContours(
            ~binarized, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE
        )
        frame_with_contours = cv.drawContours(
            image=frame.copy(),  # Because cv.drawContours modifies in-place AND returns
            contours=contours,
            contourIdx=-1,
            color=(0, 255, 0),
            thickness=3,
        )
        cv.imshow(WINDOW_NAME, frame_with_contours)
        if cv.waitKey(100) == ESC_KEY:
            break
    cap.release()


def get_frame(cap: cv.VideoCapture) -> Img[NBit_T]:
    """Get a frame from the video."""
    success, frame = cap.read()
    if not success:
        raise RuntimeError("Could not read frame")
    return frame


def get_roi(
    img: Img[NBit_T],
) -> Img[NBit_T]:
    """Get the region of interest of an image.

    See: https://docs.opencv.org/4.6.0/db/d5b/tutorial_py_mouse_handling.html
    """

    def handle_mouse_events(event: int, x: int, y: int, *_):
        """Handle all mouse events. Form a convex hull from left clicks."""
        nonlocal img, click, clicks, hull, img_composite
        if event == cv.EVENT_LBUTTONDOWN:
            click += 1
            clicks.append((x, y))
            img = cv.drawMarker(img, clicks[-1], MARKER_COLOR)
            if click == 3:
                hull = ConvexHull(clicks, incremental=True)
                img_composite = draw_hull(hull, img)
            elif click > 3:
                hull.add_points([clicks[-1]])
                img_composite = draw_hull(hull, img)
            cv.imshow(WINDOW_NAME, img_composite)

    click = 0
    clicks: list[tuple[int, int]] = []
    hull: ConvexHull = ConvexHull([(0, 0), (0, 1), (1, 0)])
    img_composite = img

    cv.imshow(WINDOW_NAME, img)
    cv.setMouseCallback(WINDOW_NAME, handle_mouse_events)
    while True and cv.waitKey(10) != ESC_KEY:
        pass
    hull.close()
    return np.array(clicks)[hull.vertices]


def draw_hull(
    hull: ConvexHull, img: npt.NDArray[np.integer[NBit_T]]
) -> npt.NDArray[np.integer[NBit_T]]:
    """Draw a convex hull on the image."""
    img = img.copy()
    clicks = hull.points.astype(int)
    for simplex in hull.simplices:
        img = cv.line(img, clicks[simplex[0]], clicks[simplex[1]], MARKER_COLOR)
    return img


if __name__ == "__main__":
    try:
        main(Params.get_params())
    finally:
        cv.destroyAllWindows()
