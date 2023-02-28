import pytest

from bot.commands import ROUTINES
from bot.instant_commands import check_health


@pytest.mark.asyncio
async def test_health_check_works():
    assert await check_health() is True


@pytest.mark.asyncio
async def test_health_check_doesnt_work(monkeypatch):
    monkeypatch.setattr(
        'tools.get_patch_prepare_data.ENDPOINTS', {'health': '/lalala'}
    )
    assert await check_health() is False


@pytest.mark.asyncio
async def test_health_check_command():
    command = 'health'
    assert await ROUTINES[command][1]() is True
