"""Show a sample image using OpenCV."""

import cv2 as cv

from boilercv import PREVIEW


def main():
    img = cv.imread(cv.samples.findFile("starry_night.jpg"))
    if PREVIEW:
        cv.imshow("Display window", img)
        cv.waitKey()
        cv.destroyAllWindows()


if __name__ == "__main__":
    main()
