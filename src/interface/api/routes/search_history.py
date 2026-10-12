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
    artist_user_id: UUID | None = None


class SearchEntry(BaseModel):
    search_history_id: UUID
    query: str
    normalized_query: str
    last_searched_at: datetime
    artist_user_id: UUID | None = None
    artist_name: str | None = None


async def entries(session: AsyncSession, user_id: UUID) -> list[SearchEntry]:
    rows = (await session.execute(text("select search_history_id,query,normalized_query,last_searched_at,artist_user_id,artist_name from search_history where user_id=:user_id order by last_searched_at desc,search_history_id desc limit 20"), {"user_id": user_id})).mappings().all()
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
    artist_name = None
    if request.artist_user_id is not None:
        artist_name = await session.scalar(text("select p.full_name from user_profiles p join user_accounts a on a.user_id=p.user_id where a.user_id=:artist_id and a.account_status='active'"), {"artist_id": request.artist_user_id})
        if artist_name is None:
            raise HTTPException(404, "Selected artist is unavailable.")
    await session.execute(text("insert into search_history(user_id,query,normalized_query,last_searched_at,artist_user_id,artist_name) values(:user_id,:query,:normalized,clock_timestamp(),:artist_id,:artist_name) on conflict(user_id,normalized_query) do update set query=excluded.query,artist_user_id=excluded.artist_user_id,artist_name=excluded.artist_name,last_searched_at=clock_timestamp()"), {"user_id": actor.user_id, "query": query, "normalized": normalized, "artist_id": request.artist_user_id, "artist_name": artist_name})
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
