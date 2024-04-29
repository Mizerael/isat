from PIL import Image, ImageFilter
import cv2
import numpy as np
import httpx
import json


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


def convert_to_cv2_image(
    image: bytes, flags: int = cv2.IMREAD_UNCHANGED
) -> cv2.typing.MatLike:
    image_array = np.frombuffer(image, dtype=np.uint8)
    return cv2.imdecode(image_array, flags)


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


async def find_by_template(
    client: httpx.AsyncClient, app_config: dict, template: cv2.typing.MatLike
) -> list[str]:
    response = await client.get(f"{app_config['loader']['link']}/image_list")
    images_name_list = json.loads(response.content.decode("utf-8"))
    find_images_list: list[str] = []
    for image_name in images_name_list["images"]:
        response = await client.get(
            f"{app_config['loader']['link']}/get_image?image_name={image_name}"
        )
        image = convert_to_cv2_image(image=response.content, flags=cv2.IMREAD_COLOR)
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(image_gray, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.6
        loc = np.where(res >= threshold)
        if len(loc[0]) > 0:
            find_images_list.append(image_name)
    return find_images_list
