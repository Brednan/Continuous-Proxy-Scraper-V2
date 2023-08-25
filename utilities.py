import datetime


def get_date_time_str():
    current_date_time = datetime.datetime.now()

    return f'{current_date_time.year}/{current_date_time.month:02d}/{current_date_time.day:02d} {current_date_time.hour:02d}:' \
           f'{current_date_time.minute:02d}'
