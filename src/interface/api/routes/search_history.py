from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.postgres.session import get_database_session
from src.interface.dependencies.authorization import Principal, require_permission

router = APIRouter(prefix="/search-history", tags=["search-history"])
Actor = Annotated[Principal, Depends(require_permission("profile.read_own"))]
Database = Annotated[AsyncSession, Depends(get_database_session)]


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)


class SearchEntry(BaseModel):
    search_history_id: UUID
    query: str
    normalized_query: str
    last_searched_at: datetime


async def entries(session: AsyncSession, user_id: UUID) -> list[SearchEntry]:
    rows = (await session.execute(text("select search_history_id,query,normalized_query,last_searched_at from search_history where user_id=:user_id order by last_searched_at desc,search_history_id desc limit 20"), {"user_id": user_id})).mappings().all()
    return [SearchEntry(**row) for row in rows]


async def lock_user(session: AsyncSession, user_id: UUID) -> None:
    # Serialize inserts and deletes per account, including retention cleanup.
    found = await session.scalar(text("select user_id from user_accounts where user_id=:user_id and account_status='active' for update"), {"user_id": user_id})
    if found is None:
        raise HTTPException(403, "Account unavailable.")


@router.get("", response_model=list[SearchEntry])
async def get_history(actor: Actor, session: Database) -> list[SearchEntry]:
    await lock_user(session, actor.user_id)
    return await entries(session, actor.user_id)


@router.post("", response_model=list[SearchEntry])
async def record_search(request: SearchRequest, actor: Actor, session: Database) -> list[SearchEntry]:
    query = request.query.strip()
    if not query:
        raise HTTPException(422, "Search query cannot be empty.")
    normalized = query.lower()
    await lock_user(session, actor.user_id)
    await session.execute(text("insert into search_history(user_id,query,normalized_query,last_searched_at) values(:user_id,:query,:normalized,clock_timestamp()) on conflict(user_id,normalized_query) do update set query=excluded.query,last_searched_at=clock_timestamp()"), {"user_id": actor.user_id, "query": query, "normalized": normalized})
    await session.execute(text("delete from search_history where user_id=:user_id and search_history_id in (select search_history_id from search_history where user_id=:user_id order by last_searched_at desc,search_history_id desc offset 20)"), {"user_id": actor.user_id})
    result = await entries(session, actor.user_id)
    await session.commit()
    return result


@router.delete("", status_code=204)
async def clear_history(actor: Actor, session: Database) -> Response:
    await lock_user(session, actor.user_id)
    await session.execute(text("delete from search_history where user_id=:user_id"), {"user_id": actor.user_id})
    await session.commit()
    return Response(status_code=204)


@router.delete("/{entry_id}", status_code=204)
async def remove_search(entry_id: UUID, actor: Actor, session: Database) -> Response:
    await lock_user(session, actor.user_id)
    await session.execute(text("delete from search_history where user_id=:user_id and search_history_id=:entry_id"), {"user_id": actor.user_id, "entry_id": entry_id})
    await session.commit()
    return Response(status_code=204)
