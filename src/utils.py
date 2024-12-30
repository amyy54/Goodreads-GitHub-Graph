from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from objects import Status
from random import randint
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")


def print_log_with_timestamp(process: str, text: str) -> None:
    logger = logging.getLogger(__name__)
    logger.info(f"[{process}] {text}")


def offset_datetime(date_str: str, timezone: str) -> datetime:
    pub_date = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
    try:
        return pub_date.astimezone(ZoneInfo(timezone))
    except ZoneInfoNotFoundError:
        return pub_date


def generate_contribution_chart(
    status: list[Status], random: bool = False, timezone: str = ""
) -> list[dict]:
    today = datetime.today()
    if len(timezone) > 0:
        try:
            today = today.astimezone(ZoneInfo(timezone))
        except ZoneInfoNotFoundError:
            pass

    current_year = today.year
    first_day_of_year = datetime(current_year, 1, 1)

    first_sunday = first_day_of_year - timedelta(first_day_of_year.weekday() + 1)

    chart_data = []
    current_day = first_sunday
    for _ in range(53 * 7):
        date_str = current_day.strftime("%Y-%m-%d")
        if current_day.year == current_year:
            count = 0
            level = 0
            if random:
                count = randint(0, 7)
            else:
                for entry in status:
                    if entry.gr_date.strftime("%Y-%m-%d") == date_str:
                        count += 1

            if count > 5:
                level = 3
            elif count > 3:
                level = 2
            elif count > 0:
                level = 1

            chart_data.append({"date": date_str, "level": level})
        else:
            chart_data.append({"date": date_str, "level": -1})
        current_day += timedelta(days=1)

    return chart_data


def generate_data_list(statuses: list[Status], timezone: str = "") -> dict:
    today = datetime.today()
    if len(timezone) > 0:
        try:
            today = today.astimezone(ZoneInfo(timezone))
        except ZoneInfoNotFoundError:
            pass

    res = {}
    for status in statuses:
        if status.gr_date.year == today.year:
            date_obj = status.gr_date.date()
            if date_obj in res.keys():
                res[date_obj].append(status)
            else:
                res[date_obj] = [status]
    return res
