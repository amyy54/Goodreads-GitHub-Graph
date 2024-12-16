from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from objects import Status


def print_log_with_timestamp(process: str, text: str) -> None:
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{time} | [{process}] {text}")


def offset_datetime(date_str: str, timezone: str) -> datetime:
    pub_date = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
    try:
        return pub_date.astimezone(ZoneInfo(timezone))
    except ZoneInfoNotFoundError:
        return pub_date


def generate_contribution_chart(status: list[Status]) -> list[dict]:
    today = datetime.today()
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
