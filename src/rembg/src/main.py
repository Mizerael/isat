import logging
from PIL import Image
from fastapi import FastAPI, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import io
from utils import rembg
from resources.config import configure_logging, get_config

configure_logging()

app_config = get_config("config/app.json")
rembg_ctx = get_config(app_config["rembg"]["config"])

logger = logging.getLogger("rembg")

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
