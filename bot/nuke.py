from typing import Tuple


def parse_nuke_command(command: str) -> Tuple[str, int]:
    _, ticker, sum = command.split()
    return ticker.upper(), int(sum)
