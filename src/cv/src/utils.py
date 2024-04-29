from PIL import Image, ImageFilter
import cv2


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


def add_background(
    background_img: cv2.typing.MatLike, overlay_img: cv2.typing.MatLike
) -> bytes:
    height, width, _ = overlay_img.shape
    background_img = cv2.resize(background_img, (width, height))
    for y in range(height):
        for x in range(width):
            overlay_color = overlay_img[y, x, :3]
            overlay_alpha = overlay_img[y, x, 3] / 255
            background_color = background_img[y, x]
            composite_color = (
                background_color * (1 - overlay_alpha) + overlay_color * overlay_alpha
            )
            background_img[y, x] = composite_color

    _, background_img_bytes = cv2.imencode(".png", background_img)
    return background_img_bytes.tobytes()
