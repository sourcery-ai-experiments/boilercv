import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import ConvexHull

IMG_DTYPE = np.int8
ESC_KEY = ord("\x1b")


def main():
    cap = cv.VideoCapture("data/in/results_2022-04-08T16-12-42.mp4")
    while cap.isOpened():
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        binarized = cv.adaptiveThreshold(
            gray, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2
        )
        contours, hierarchy = cv.findContours(
            binarized, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE
        )
        frame_with_contours = cv.drawContours(
            image=frame.copy(),  # because cv.drawContours modifies in-place AND returns
            contours=contours,
            contourIdx=-1,
            color=(0, 255, 0),
            thickness=3,
        )
        cv.imshow("contours", frame_with_contours)
        if cv.waitKey(100) == ord("q"):
            break
    cap.release()


def get_roi():
    """
    Get points from mouse clicks.

    See: https://docs.opencv.org/4.6.0/db/d5b/tutorial_py_mouse_handling.html
    """

    clicks = []

    def get_xy(event, x, y, flags, param):
        nonlocal clicks
        if event == cv.EVENT_LBUTTONDOWN:
            clicks.append((x, y))

    img = np.zeros((512, 512, 3), np.uint8)
    cv.namedWindow("image")
    cv.setMouseCallback("image", get_xy)
    while True:
        cv.imshow("image", img)
        if cv.waitKey(10) == ESC_KEY:
            break

    coords = np.array(clicks, dtype=IMG_DTYPE)
    hull = ConvexHull(coords)

    # TODO: Implement fillConvexPoly()
    # See: https://docs.opencv.org/4.6.0/d6/d6e/group__imgproc__draw.html#ga9bb982be9d641dc51edd5e8ae3624e1f
    # * ---------------------------------------------------------------------------- * #
    # * See: https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.ConvexHull.html
    plt.plot(coords[:, 0], coords[:, 1], "o")
    for simplex in hull.simplices:
        plt.plot(coords[simplex, 0], coords[simplex, 1], "k-")
    plt.show()
    # * ---------------------------------------------------------------------------- * #
    ...


if __name__ == "__main__":
    main()
    # hull = get_roi()
    cv.destroyAllWindows()
