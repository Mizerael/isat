import httpx
import asyncio
from fastapi import FastAPI
from bs4 import BeautifulSoup
from resources.config import get_config, configure_logging
import logging
import json

configure_logging()

app_config = get_config("config/app.json")
steam_ctx = get_config(app_config["crawler"]["config"])

crawler = FastAPI()

logger = logging.getLogger("crawler")


async def get_items_link(
    http_session: httpx.AsyncClient,
    ctx: any,
    logger: logging.Logger,
    main_queue: asyncio.Queue,
    pages_queue: asyncio.Queue,
    exp_delay: int,
) -> None:
    i = await pages_queue.get()
    logger.info(f"GET items links from {ctx['link_xhr']}&start={i*10}")
    response = await http_session.get(
        f"{ctx['link_xhr']}&start={i*10}&count={ctx['count']}"
        + f"&search_descriptions={ctx['search_description']}"
        + f"&sort_column={ctx['sort_column']}&sort_dir={ctx['sort_dir']}"
        + f"&appid={ctx['appid']}"
    )
    if response.status_code == 200:
        json_data = json.loads(response.content)
        content = json_data["results_html"]
        soup = BeautifulSoup(content, "html.parser")
        items = soup.find_all("a", class_="market_listing_row_link")
        for item in items:
            item_link = item.get("href")
            await main_queue.put(item_link)
        pages_queue.task_done()
    else:
        logger.error(f"GET {ctx['link_xhr']}&start={i*10} {response.status_code}")
        await pages_queue.put(i)
        await asyncio.sleep(exp_delay * 15)
        asyncio.create_task(get_items_link(http_session, ctx, logger, i, exp_delay * 2))


async def pages_link(
    http_session: httpx.AsyncClient,
    ctx: any,
    logger: logging.Logger,
    main_queue: asyncio.Queue,
    count_items: int,
):
    pages_queue = asyncio.Queue(maxsize=1)
    for i in range(count_items // ctx["count"]):
        await pages_queue.put(i)
        await get_items_link(
            http_session,
            ctx,
            logger,
            main_queue,
            pages_queue,
            1,
        )
        await pages_queue.join()
        await asyncio.sleep(2.0)
