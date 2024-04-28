import httpx
import asyncio
from bs4 import BeautifulSoup
import logging
import json


async def get_items_link(
    http_session: httpx.AsyncClient,
    ctx: any,
    logger: logging.Logger,
    queue_link: str,
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
            try:
                timeout = httpx.Timeout(None)
                await http_session.post(
                    url=queue_link + f"?link={item_link}", timeout=timeout
                )
            except httpx.ConnectError as e:
                logger.error(f"POST {queue_link} {e}")
        pages_queue.task_done()
    else:
        logger.error(f"GET {ctx['link_xhr']}&start={i*10} {response.status_code}")
        await pages_queue.put(i)
        await asyncio.sleep(exp_delay * 15)
        await get_items_link(
            http_session=http_session,
            ctx=ctx,
            logger=logger,
            queue_link=queue_link,
            pages_queue=pages_queue,
            exp_delay=exp_delay * 2,
        )


async def pages_link(
    http_session: httpx.Client,
    ctx: any,
    logger: logging.Logger,
    queue_link: str,
    count_items: int,
):
    pages_queue = asyncio.Queue(maxsize=1)
    for i in range(count_items // ctx["count"]):
        await pages_queue.put(i)
        await get_items_link(
            http_session=http_session,
            ctx=ctx,
            logger=logger,
            queue_link=queue_link + "/add_to_queue",
            pages_queue=pages_queue,
            exp_delay=1,
        )
        await pages_queue.join()
        await asyncio.sleep(2.0)
