from bot.nuke import parse_nuke_command


def test_parse_nuke_command():
    assert parse_nuke_command('/nuke gazp 10000') == ('GAZP', 10000)
