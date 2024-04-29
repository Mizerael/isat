from PIL import Image, ImageFilter


def erode(cycles, image):
    for _ in range(cycles):
        image = image.filter(ImageFilter.MinFilter(3))
    return image


def dilate(cycles, image):
    for _ in range(cycles):
        image = image.filter(ImageFilter.MaxFilter(3))
    return image


def rembg(img: Image.Image, treshold: int) -> Image.Image:
    colors = img.split()
    selected_color = colors[2]
    img_treshold = selected_color.point(lambda x: 255 if x < treshold else 0).convert(
        "1"
    )
    dilate_img = dilate(5, img_treshold)
    mask = erode(5, dilate_img)
    mask = mask.convert("L").filter(ImageFilter.BoxBlur(3))
    blank = img.point(lambda _: 0)
    segmented_img = Image.composite(img, blank, mask)
    return segmented_img
