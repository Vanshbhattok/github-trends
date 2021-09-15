from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, Response, status

from src.db.models.users import UserModel as DBUserModel
from src.db.functions.users import login_user, update_user
from src.db.functions.get import get_user_by_user_id

from src.packaging.user import main as get_data
from src.analytics.user.commits import get_top_languages, get_top_repos
from src.analytics.user.contribs_per_day import (
    get_contribs_per_day,
    get_contribs_per_repo_per_day,
)

from src.utils import async_fail_gracefully

router = APIRouter()


@router.get("/db/create/{user_id}/{access_token}", status_code=status.HTTP_200_OK)
@async_fail_gracefully
async def create_user_endpoint(
    response: Response, user_id: str, access_token: str
) -> str:
    return await login_user(user_id, access_token)


@router.get("/db/get/{user_id}", status_code=status.HTTP_200_OK)
@async_fail_gracefully
async def get_user_endpoint(response: Response, user_id: str) -> Optional[DBUserModel]:
    return await get_user_by_user_id(user_id)


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
@async_fail_gracefully
async def get_user(
    response: Response,
    user_id: str,
    start_date: date = date.today() - timedelta(365),
    end_date: date = date.today(),
    timezone_str: str = "US/Eastern",
) -> Dict[str, Any]:
    db_user = await get_user_by_user_id(user_id)
    if db_user is None or db_user.access_token == "":
        raise LookupError("Invalid UserId")

    if db_user.raw_data is not None and (
        datetime.now() - db_user.last_updated
    ) < timedelta(hours=6):
        return db_user.raw_data

    data = await get_data(
        user_id, db_user.access_token, start_date, end_date, timezone_str
    )

    top_languages = get_top_languages(data)
    top_repos = get_top_repos(data)
    contribs_per_day = get_contribs_per_day(data)
    contribs_per_repo_per_day = get_contribs_per_repo_per_day(data)

    output = {
        "top_languages": top_languages,
        "top_repos": top_repos,
        "contribs_per_day": contribs_per_day,
        "contribs_per_repo_per_day": contribs_per_repo_per_day,
    }

    await update_user(user_id, output)

    return output