from proxy_scraper import *
from database import ProxyDatabase
import os
from utilities import *
import time


if __name__ == '__main__':
    env_vars = os.environ

    with open('./mysql.txt', 'r') as f:
        content = f.read().split('\n')
        mysql_ip = content[0]
        mysql_username = content[1]

    while True:
        print(f'{get_date_time_str()} - Starting proxy scrape')

        proxies = scrape_proxies()
        database = ProxyDatabase(mysql_ip, mysql_username, env_vars.get('mysql_pass'))
        print(f'{get_date_time_str()} - Finished proxy scrape')

        database.add_proxies(proxies)

        time.sleep(60*20)
