import httpx
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


def sub_load(query_link: str, loader_link: str):
    with httpx.Client() as client:
        response = client.get(query_link + "/get_from_queue")
        time.sleep(2.0)
        if response.status_code == 200:
            link = response.content.decode("utf-8")[1:-1]
            client.get(
                f"{loader_link}/load_image?link={link}&exp_delay=1",
                timeout=httpx.Timeout(None),
            )
            time.sleep(2.0)


def load_link(crawler_link: str, count: int):
    with httpx.Client() as client:
        post_link = f"{crawler_link}/scrape?count={count}"
        timeout = httpx.Timeout(None)
        client.post(url=post_link, timeout=timeout)


async def load_image(
    crawler_link: str,
    loader_link: str,
    query_link: str,
    logger: logging.Logger,
    count: int,
    count_worker: int,
):
    with ThreadPoolExecutor(max_workers=count_worker) as executor:
        results = {
            executor.submit(load_link, crawler_link, count): 0,
            **{
                executor.submit(sub_load, query_link, loader_link): i
                for i in range(1, count + 1)
            },
        }
        for result in as_completed(results):
            id = results[result]
            try:
                _ = result.result()
            except Exception as exc:
                logger.error(f"{id} вызвало исключение: {exc}")
