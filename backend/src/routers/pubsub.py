from typing import Any

from fastapi import APIRouter, Response, Request, status

from src.external.pubsub.templates import publish_to_topic, parse_request
from src.utils import fail_gracefully, async_fail_gracefully

router = APIRouter()

count: int = 0


@router.get("/test", status_code=status.HTTP_200_OK)
@fail_gracefully
def test(response: Response) -> Any:
    return {"test": count}


@router.get("/pub/test/{update}", status_code=status.HTTP_200_OK)
@fail_gracefully
def test_post(response: Response, update: str) -> Any:
    publish_to_topic("test", {"num": int(update)})
    return update


@router.post("/sub/test/{token}", status_code=status.HTTP_200_OK)
@async_fail_gracefully
async def test_pubsub(response: Response, token: str, request: Request) -> Any:
    data = await parse_request(token, request)

    global count
    count += data["num"]