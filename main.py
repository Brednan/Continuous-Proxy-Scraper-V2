from proxy_scraper import *
from database import ProxyDatabase
from utilities import *
import time


if __name__ == '__main__':
    mysql_ip, mysql_username, mysql_password = get_database_credentials()

    while True:
        print(f'{get_date_time_str()} - Starting proxy scrape')

        proxies = scrape_proxies()
        print(f'{get_date_time_str()} - Finished proxy scrape')

        database = ProxyDatabase(mysql_ip, mysql_username, mysql_password)
        database.add_proxies(proxies)

        time.sleep(60*20)
