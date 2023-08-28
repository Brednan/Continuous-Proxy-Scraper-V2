import os
import datetime


def get_date_time_str():
    current_date_time = datetime.datetime.now()

    return f'{current_date_time.year}/{current_date_time.month:02d}/{current_date_time.day:02d} {current_date_time.hour:02d}:' \
           f'{current_date_time.minute:02d}'


def get_database_credentials() -> tuple:
    with open('./mysql.txt', 'r') as f:
        content = f.read().split('\n')
        mysql_ip = content[0]
        mysql_username = content[1]

    env_vars = os.environ
    return mysql_ip, mysql_username, env_vars.get('mysql_pass')
