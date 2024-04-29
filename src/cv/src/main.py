import logging
from PIL import Image
from fastapi import FastAPI, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import cv2
import io
from utils import rembg, add_background, convert_to_cv2_image, find_by_template
from resources.config import configure_logging, get_config

configure_logging()

app_config = get_config("config/app.json")
rembg_ctx = get_config(app_config["cv"]["config"])

logger = logging.getLogger("cv")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = httpx.AsyncClient(
    headers={
        "User-Agent": "learningProject",
    }
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post(
    "/rembg",
)
async def remove_background(file: UploadFile):
    image = Image.open(io.BytesIO(await file.read()))
    content = rembg(img=image, treshold=rembg_ctx["treshold"])
    img_buffer = io.BytesIO()
    content.save(img_buffer, format="PNG")

    return StreamingResponse(io.BytesIO(img_buffer.getvalue()), media_type="image/png")


@app.post("/paste_to_image")
async def paste_to_image(background_file: UploadFile, overlay_file: UploadFile):
    background_img = convert_to_cv2_image(image=await background_file.read())
    overlay_img = convert_to_cv2_image(image=await overlay_file.read())

    result_image_bytes = add_background(
        background_img=background_img, overlay_img=overlay_img
    )

    return StreamingResponse(io.BytesIO(result_image_bytes), media_type="image/png")


@app.post("/find_by_image")
async def find_by_image(template_file: UploadFile):
    template_image = convert_to_cv2_image(
        image=await template_file.read(), flags=cv2.IMREAD_GRAYSCALE
    )
    find_images_list = await find_by_template(
        client=client, app_config=app_config, template=template_image
    )

    return JSONResponse(content={"images": find_images_list})
