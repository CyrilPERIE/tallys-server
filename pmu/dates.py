from datetime import date, datetime


def date_to_programme_date(_date: date) -> str:
    return _date.strftime("%d%m%Y")

def programme_date_to_date(programme_date: str) -> date:
    return datetime.strptime(programme_date, "%d%m%Y")