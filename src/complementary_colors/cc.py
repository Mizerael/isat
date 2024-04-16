import logging
import cv2
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from resources.config import configure_logging


class Rgb(BaseModel):
    r: int
    g: int
    b: int


configure_logging()

logger = logging.getLogger("cc")

complement_color = FastAPI()


@complement_color.get("/")
async def root():
    return {"message": "Hello World"}


@complement_color.post("/complemented_colors")
async def compute_complement(rgb: Rgb) -> Rgb:
    hls = cv2.cvtColor(
        np.array([[[rgb.r, rgb.g, rgb.b]]], dtype=np.uint8), cv2.COLOR_RGB2HLS
    )
    hue, light, sat = hls[0][0]
    logger.info(f"{hls}")
    complement_hls = cv2.cvtColor(
        np.array([[[(hue + 90) % 180, light, sat]]], dtype=np.uint8), cv2.COLOR_HLS2RGB
    )[0][0]
    logger.info(complement_hls)
    return Rgb.model_construct(
        r=int(complement_hls[0]), g=int(complement_hls[1]), b=int(complement_hls[2])
    )
