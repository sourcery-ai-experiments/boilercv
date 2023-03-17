"""Find blobs in footage."""


from boilercv import PARAMS, get_8bit_images
from boilercv.gui import get_video_images, preview_images
from boilercv.images import load_roi
from boilercv.types import ImgSeq8


def main():
    images = get_8bit_images(
        get_video_images(
            PARAMS.paths.examples_data / "results_2022-11-30T12-39-07_98C.cine"
        )
    )
    roi = load_roi(PARAMS.paths.examples_data / "roi.yaml", next(images))
    result: ImgSeq8 = []
    for image in images:
        result.append(image)
    preview_images(result)


if __name__ == "__main__":
    main()
