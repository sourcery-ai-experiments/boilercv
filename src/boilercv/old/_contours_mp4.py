"""Given an MP4, find ROI using `opencv` and find contours."""

from cv2 import COLOR_GRAY2RGB, EVENT_LBUTTONDOWN, destroyAllWindows, imshow, waitKey
from numpy import array, fliplr
from scipy.spatial import ConvexHull

from boilercv.colors import BLUE_CV
from boilercv.examples.cv import capture_images
from boilercv.images import scale_bool
from boilercv.images.cv import (
    apply_mask,
    binarize,
    build_mask_from_polygons,
    convert_image,
    draw_contours,
    drawMarker,  # pyright: ignore[reportAttributeAccessIssue]  # pyright 1.1.348, opencv-contrib-python 4.9.0.80
    find_contours,
    line,  # pyright: ignore[reportAttributeAccessIssue]  # pyright 1.1.348, opencv-contrib-python 4.9.0.80
    setMouseCallback,  # pyright: ignore[reportAttributeAccessIssue]  # pyright 1.1.348, opencv-contrib-python 4.9.0.80
)
from boilercv.models.params import PARAMS
from boilercv.types import ArrInt

WINDOW_NAME = "image"
ESC_KEY = ord("\x1b")


def main():
    images = (
        image[:, :, 0]
        for image in capture_images(
            PARAMS.paths.examples / "2022-04-08T16-12-42_short.mp4"
        )
    )
    roi = fliplr(get_roi2(next(images)))
    for image in images:
        masked = apply_mask(image, build_mask_from_polygons(image, [roi]))
        thresholded = binarize(masked)
        contours = find_contours(scale_bool(~thresholded))
        image_with_contours = draw_contours(image, contours)
        imshow(WINDOW_NAME, image_with_contours)
        if waitKey(100) == ESC_KEY:
            break
    destroyAllWindows()


def get_roi2(image: ArrInt) -> ArrInt:
    """Get the region of interest of an image.

    See: https://docs.opencv.org/4.6.0/db/d5b/tutorial_py_mouse_handling.html
    """

    clicks: list[tuple[int, int]] = []

    image = convert_image(image, COLOR_GRAY2RGB)
    (width, height) = image.shape[:-1]
    click = 0
    default_clicks = [(0, 0), (0, width), (height, width), (height, 0)]
    hull = ConvexHull(default_clicks)  # type: ignore  # pyright 1.1.333
    hull_minimum_vertices = 3
    composite_image = image

    def main() -> ArrInt:
        nonlocal clicks
        imshow(WINDOW_NAME, image)
        setMouseCallback(WINDOW_NAME, handle_mouse_events)  # type: ignore  # pyright 1.1.333
        while True and waitKey(100) != ESC_KEY:
            pass
        if len(clicks) < hull_minimum_vertices:
            clicks = default_clicks
        else:
            hull.close()
        return array(clicks)[hull.vertices]

    def handle_mouse_events(event: int, x: int, y: int, *_):
        """Handle all mouse events. Form a convex hull from left clicks."""
        nonlocal image, click, hull, composite_image
        if event == EVENT_LBUTTONDOWN:
            click += 1
            clicks.append((x, y))
            image = drawMarker(image, clicks[-1], BLUE_CV)  # type: ignore  # pyright 1.1.333
            if click == hull_minimum_vertices:
                hull = ConvexHull(clicks, incremental=True)  # type: ignore  # pyright 1.1.333
                composite_image = draw_hull(hull, image)
            elif click > hull_minimum_vertices:
                hull.add_points([clicks[-1]])
                composite_image = draw_hull(hull, image)
            imshow(WINDOW_NAME, composite_image)

    def draw_hull(hull: ConvexHull, image: ArrInt) -> ArrInt:
        """Draw a convex hull on the image."""
        image = image.copy()
        clicks = hull.points.astype(int)
        for simplex in hull.simplices:
            image = line(image, clicks[simplex[0]], clicks[simplex[1]], BLUE_CV)  # type: ignore  # pyright 1.1.333
        return image

    return main()


if __name__ == "__main__":
    main()
