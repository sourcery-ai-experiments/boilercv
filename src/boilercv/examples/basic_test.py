from os import environ
from pathlib import Path

import cv2 as cv

SAMPLES_ENV_VAR = "OPENCV_SAMPLES_DATA_PATH"


def main():
    if (
        not (samples_dir := environ.get(SAMPLES_ENV_VAR))
        or not Path(samples_dir).exists()
    ):
        raise RuntimeError(
            f"{SAMPLES_ENV_VAR} not set or specified directory does not exist."
        )
    samples_dir = Path(__file__).parent.parent.parent / "data"
    cap = cv.VideoCapture(cv.samples.findFile("vtest.avi"))
    while cap.isOpened():
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        cv.imshow("frame", gray)
        if cv.waitKey(1) == ord("q"):
            break
    cap.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
