from bot.nuke import parse_nuke_command
from bot.place_stops import sum_is_valid


def test_parse_nuke_command():
    assert parse_nuke_command('/nuke gazp 10000') == ('GAZP', 10000)


def test_process_nuke_command_with_low_sum(sample_far_leg):
    assert sum_is_valid(sample_far_leg, 100) is False
