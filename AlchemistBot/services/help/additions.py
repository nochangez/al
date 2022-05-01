# coding=utf-8


from datetime import datetime


def get_current_time():
    return datetime.now()


def format_current_time():
    return get_current_time().strftime("%d.%m.%Y %H:%M:%S")


def convert_to_date(time: str):
    try:
        return datetime.strptime(time, "%d.%m.%Y")
    except:
        return False
