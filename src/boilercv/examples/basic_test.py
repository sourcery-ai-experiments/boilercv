"""A basic test of OpenCV and sample files."""

import cv2 as cv

from boilercv import logger


def main():
    cap = cv.VideoCapture(cv.samples.findFile("vtest.avi"))
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            logger.info("Can't receive frame (stream end?). Exiting ...")
            break
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        cv.imshow("frame", gray)
        if cv.waitKey(1) == ord("q"):
            break
    cap.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
