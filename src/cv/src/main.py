import logging
from PIL import Image
from fastapi import FastAPI, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import io
from utils import rembg, add_background
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
async def paste_to_image(background: UploadFile, overlay: UploadFile):
    background_bytes = await background.read()
    background_array = np.frombuffer(background_bytes, dtype=np.uint8)
    background_img = cv2.imdecode(background_array, cv2.IMREAD_UNCHANGED)

    overlay_bytes = await overlay.read()
    overlay_array = np.frombuffer(overlay_bytes, dtype=np.uint8)
    overlay_img = cv2.imdecode(overlay_array, cv2.IMREAD_UNCHANGED)

    result_image_bytes = add_background(
        background_img=background_img, overlay_img=overlay_img
    )

    return StreamingResponse(io.BytesIO(result_image_bytes), media_type="image/png")
