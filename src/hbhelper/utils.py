import datetime

QUARTERS = ["q1", "q2", "q3", "q4"]

MONTHS = [
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
]


def is_year(date: str) -> bool:
    return date.isnumeric() and 1900 <= int(date) <= 2100


def is_quarter(date: str) -> bool:
    return date.lower() in QUARTERS


def is_month(date: str) -> bool:
    return date.lower() in MONTHS


def to_year(date: str) -> int:
    assert is_year(date)
    return int(date)


def to_quarter(date: str) -> int:
    assert is_quarter(date)
    return int(date[1:])


def to_month(date: str) -> int:
    assert is_month(date)
    return MONTHS.index(date.lower()[:3]) + 1


def get_quarter(
    quarter: int, year: int | None = None
) -> tuple[datetime.date, datetime.date]:
    if year is None:
        today = datetime.date.today()
        current_month = today.month
        current_year = today.year
        current_quarter = 1 + current_month // 4

        if quarter > current_quarter:
            year = current_year - 1
        else:
            year = current_year

    begin = datetime.date(year, 3 * quarter - 2, 1)
    end = datetime.date(year + quarter // 4, 3 * (quarter % 4) + 1, 1)

    return begin, end


def get_month(
    month: int, year: int | None = None
) -> tuple[datetime.date, datetime.date]:
    if year is None:
        today = datetime.date.today()
        current_month = today.month
        current_year = today.year
        if month > current_month:
            year = current_year - 1
        else:
            year = current_year

    begin = datetime.date(year, month, 1)
    end = datetime.date(year + month // 12, month % 12 + 1, 1)

    return begin, end


def get_begin_and_end_from_dates(
    dates: tuple[str, ...],
) -> tuple[datetime.date, datetime.date]:
    """
    Parse the dates and return the begin and end dates (end is exclusive)

    Uses the following format:

    _ => everything
    2024 => whole 2024
    2024 q1 => Q1 of 2024
    2024 jan => january 2024
    q1 => latest Q1
    jan => latest january

    The order of the tokens does not matter.
    """

    dates = tuple(sorted(dates))

    if len(dates) == 0:
        return datetime.date(1900, 1, 1), datetime.date(2100, 1, 1)

    if len(dates) == 1:
        date = dates[0]

        if is_year(date):
            year = to_year(date)
            return datetime.date(year, 1, 1), datetime.date(year + 1, 1, 1)
        if is_quarter(date):
            quarter = to_quarter(date)
            return get_quarter(quarter)
        if is_month(date):
            month = to_month(date)
            return get_month(month)

        raise Exception("Unexpected date specifier")

    if len(dates) == 2:
        if not is_year(dates[0]):
            raise Exception("Expected a year")

        year = to_year(dates[0])

        if is_year(dates[1]):
            raise Exception("Two year specifiers")
        if is_quarter(dates[1]):
            quarter = to_quarter(dates[1])
            return get_quarter(quarter, year)
        if is_month(dates[1]):
            month = to_month(dates[1])
            return get_month(month, year)

        raise Exception("Unexpected date specifier")

    raise Exception("Too many date specifiers")
