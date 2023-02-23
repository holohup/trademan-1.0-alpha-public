from datetime import datetime, timedelta, timezone
from decimal import Decimal

from settings import OFFSET_ADJUSTED_WORK_HOURS, WORK_DAYS, ZONE
from tinkoff.invest.schemas import Quotation
from tinkoff.invest.utils import decimal_to_quotation


def get_correct_price(price: Decimal, increment: Decimal) -> Quotation:
    answer = price // increment * increment
    return decimal_to_quotation(answer)


def get_lots(number_of_stocks, lot):
    return number_of_stocks // lot


def delta_minutes_to_utc(minutes):
    return datetime.now(tz=timezone.utc) + timedelta(minutes=minutes)


# time management block


def get_open_and_close_time(func):  # min = open time, max = close time
    hours_values = [
        t for tupl in OFFSET_ADJUSTED_WORK_HOURS.values() for t in tupl
    ]
    return func(hours_values)


def perform_working_hours_check() -> bool:
    current_time = datetime.now(ZONE)
    if (
        current_time.weekday() < WORK_DAYS[0]
        or current_time.weekday() > WORK_DAYS[1]
    ):
        return False
    for session_open, session_close in OFFSET_ADJUSTED_WORK_HOURS.values():
        if session_open <= current_time.time() <= session_close:
            return True
    return False


def seconds_till_open_from_midnight() -> int:
    open_time = get_open_and_close_time(min)
    return open_time.hour * 60 * 60 + open_time.minute * 60 + open_time.second


def seconds_till_midnight(current_time: datetime) -> int:
    return (
        ((24 - current_time.hour - 1) * 60 * 60)
        + ((60 - current_time.minute - 1) * 60)
        + (60 - current_time.second)
    )


def get_midnights_to_wait(current_time: datetime) -> int:
    if (
        current_time.weekday() < WORK_DAYS[0]
        or current_time.weekday() > WORK_DAYS[1]
        or (
            current_time.weekday() == WORK_DAYS[1]
            and current_time.time() >= get_open_and_close_time(max)
        )
    ):
        return 7 - current_time.weekday() + WORK_DAYS[0]
    if current_time.time() >= get_open_and_close_time(max):
        return 1
    return 0


def get_seconds_till_open() -> int:
    current_time = datetime.now(ZONE)
    midnights = get_midnights_to_wait(current_time)
    if midnights > 0:
        return (
            (midnights - 1) * 24 * 60 * 60
            + seconds_till_midnight(current_time)
            + seconds_till_open_from_midnight()
        )

    sess_start_times = [
        period[0] for period in OFFSET_ADJUSTED_WORK_HOURS.values()
    ]
    time_deltas_till_open = [
        (
            datetime.combine(current_time.date(), session_start_time)
            - datetime.combine(current_time.date(), current_time.time())
        )
        for session_start_time in sess_start_times
    ]
    time_deltas_till_open = [
        time_delta
        for time_delta in time_deltas_till_open
        if time_delta > timedelta(0)
    ]
    minimum_delta = min(time_deltas_till_open)
    return minimum_delta.seconds + 1
