import pytest

from bot.commands import tasks


@pytest.mark.asyncio
async def test_tasks_return_none_with_no_tasks():
    assert await tasks() == 'Running tasks: None'
