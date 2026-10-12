from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from typing import cast

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.enums.role import Role
from src.interface.dependencies.authorization import Principal
from src.interface.api.routes.search_history import SearchRequest, record_search, remove_search


@pytest.mark.asyncio
async def test_record_normalizes_query_and_serializes_retention() -> None:
    actor = Principal(uuid4(), Role.USER, frozenset({"profile.read_own"}))
    db = AsyncMock(spec=AsyncSession)
    db.scalar.return_value = actor.user_id
    result = MagicMock()
    result.mappings.return_value.all.return_value = []
    db.execute.return_value = result
    await record_search(SearchRequest(query=" ANIME ART "), actor, cast(AsyncSession, db))
    assert "for update" in str(db.scalar.call_args.args[0])
    assert db.execute.call_args_list[0].args[1] == {"user_id": actor.user_id, "query": "ANIME ART", "normalized": "anime art"}
    assert "on conflict" in str(db.execute.call_args_list[0].args[0])
    assert "offset 20" in str(db.execute.call_args_list[1].args[0])
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_blank_search_does_not_write() -> None:
    db = AsyncMock(spec=AsyncSession)
    with pytest.raises(HTTPException):
        await record_search(SearchRequest(query="   "), Principal(uuid4(), Role.USER, frozenset()), cast(AsyncSession, db))
    db.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_is_scoped_to_authenticated_account() -> None:
    actor = Principal(uuid4(), Role.USER, frozenset())
    db = AsyncMock(spec=AsyncSession)
    db.scalar.return_value = actor.user_id
    entry_id = uuid4()
    await remove_search(entry_id, actor, cast(AsyncSession, db))
    assert db.execute.call_args.args[1] == {"user_id": actor.user_id, "entry_id": entry_id}
    assert "user_id=:user_id" in str(db.execute.call_args.args[0])
