"""Preview of a processed example from the dataset."""


import xarray as xr

# from matplotlib import pyplot as plt
# # from scipy.ndimage import generate_binary_structure, label
# from skimage.color import label2rgb
# from skimage.measure import label
from boilercv import PREVIEW
from boilercv.data import VIDEO
from boilercv.data.sets import get_contours_df
from boilercv.gui import view_images
from boilercv.models.params import PARAMS

EXAMPLE = ["2021-02-23T14-27-59"]


def main():
    contours = get_contours_df(*EXAMPLE)
    gray = xr.open_dataset(PARAMS.paths.gray_preview)[VIDEO].sel(video_name=EXAMPLE)
    filled = xr.open_dataset(PARAMS.paths.filled_preview)[VIDEO].sel(video_name=EXAMPLE)
    # label_image = label(filled.squeeze().values)
    # to make the background transparent, pass the value of `bg_label`,
    # and leave `bg_color` as `None` and `kind` as `overlay`
    # image_label_overlay = label2rgb(
    #     label_image, image=gray.squeeze().values, bg_label=0
    # )

    # fig, ax = plt.subplots(figsize=(10, 6))
    # ax.imshow(image_label_overlay)
    # plt.show()
    # ...
    # colored = xr.apply_ufunc(
    #     label2rgb,
    #     labeled_img,
    #     gray3,
    #     input_core_dims=(YX_PX, [*YX_PX, "channel"]),
    #     output_core_dims=([*YX_PX, "channel"],),
    #     vectorize=True,
    #     kwargs=dict(bg_label=0),
    # )
    # colored = label2rgb(labeled_img.values, gray)
    # num_objects = int(labeled_img.max())
    # composite_da = gray
    # for obj in range(1, num_objects + 1):
    #     filtered_img = labeled_img == obj
    #     compose_da(composite_da, scale_bool(filtered_img)).transpose(
    #         "video_name", "ypx", "xpx", "channel"
    #     )
    # composite_da = draw_text_da(composite_da)
    if PREVIEW:
        view_images(filled)


# def temp(img: ImgLike):
#     find_diag_conns = generate_binary_structure(rank=2, connectivity=2)
#     labeled_img, num_objects = label(input=img, structure=find_diag_conns)
#     return labeled_img


if __name__ == "__main__":
    main()
