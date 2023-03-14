"""Import frames from a cine file."""

import cv2
from pycine.raw import read_frames


def imshow(img):
    _, ret = cv2.imencode(".jpg", img * 255)
    cv2.imshow("image", ret)


def main():
    raw_images, *_ = read_frames(
        cine_file="C:/Users/Blake/Desktop/test/results_2022-01-06T13-23-39.cine",
        start_frame=0,
        count=10,
    )
    for _image in raw_images:
        ...


if __name__ == "__main__":
    main()
