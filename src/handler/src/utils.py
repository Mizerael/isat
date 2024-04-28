import httpx
import logging


async def load_image(loader_link: str, logger: logging.Logger, count: int):
    client = httpx.AsyncClient()
    timeout = httpx.Timeout(None)
    client.post(f"{loader_link}/load_image?count={count}&exp_delay=1", timeout=timeout)
