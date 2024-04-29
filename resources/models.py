from pydantic import BaseModel


class Rgb(BaseModel):
    r: int
    g: int
    b: int
