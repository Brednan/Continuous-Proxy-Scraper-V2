import requests
import selenium.common.exceptions
from bs4 import BeautifulSoup
from proxy import Proxy, filter_duplicate_proxies,ProxyParametersNullException
from utilities import get_date_time_str, get_database_credentials
from database import ProxyDatabase
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException


def scrape_free_proxy_list():
    proxies = []

    res = requests.get('https://free-proxy-list.net/')
    soup = BeautifulSoup(res.content, 'html5lib')

    table_body = soup.find('table').find('tbody')

    for row in table_body.findAll('tr'):
        ip = row.findNext('td').text
        port = row.findNext('td').findNext('td').text
        anonymity_level = row.findNext('td').findNext('td').findNext('td').findNext('td').findNext('td').text
        https = row.findNext('td').findNext('td').findNext('td').findNext('td').findNext('td').findNext('td').findNext('td').text

        if anonymity_level == 'elite proxy':
            anonymity_level = 'elite'

        if https == 'yes':
            protocol = 'https'
        else:
            protocol = 'http'

        proxies.append(Proxy(ip, port, protocol, anonymity_level))

    print(f'{get_date_time_str()} - Finished scraping proxies from Free Proxy List')
    return proxies


def scrape_geonode_proxies() -> list:
    proxies = []

    page_num = 1
    while True:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.'
                          '0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://geonode.com',
            'Referer': 'https://geonode.com/'
        }

        try:
            res = requests.get(
                f'https://proxylist.geonode.com/api/proxy-list?limit=500&page={page_num}&sort_by=lastChecke'
                f'd&sort_type=desc', headers=headers, timeout=10)

            res_json = res.json()
            if not res_json:
                break

            proxy_list = res_json.get('data')

            if not proxy_list or len(proxy_list) <= 0:
                break

            for item in proxy_list:
                proxies.append(Proxy(item['ip'], item['port'], item['protocols'][0], item['anonymityLevel']))

            page_num += 1

        except (requests.exceptions.JSONDecodeError, requests.exceptions.ReadTimeout):
            break

    print(f'{get_date_time_str()} - Finished scraping proxies from Geonode')
    return proxies


def scrape_proxyscrape_proxies() -> list:
    proxies = []

    data = requests.get('https://api.proxyscrape.com/proxytable.php?nf=true&country=all').json()

    http_proxies = list(data['http'].keys())
    http_proxy_info = list(data['http'].values())

    socks4_proxies = list(data['socks4'].keys())
    socks4_proxy_info = list(data['socks4'].values())

    socks5_proxies = list(data['socks5'].keys())
    socks5_proxy_info = list(data['socks5'].values())

    i = 0
    while i < len(http_proxies):
        ip_and_port = http_proxies[i].split(':')
        anonymity_level = int(http_proxy_info[i]['anonymity'])

        if anonymity_level == 3:
            anonymity = 'elite'
        elif anonymity_level == 2:
            anonymity = 'anonymous'
        else:
            anonymity = 'transparent'

        proxies.append(Proxy(ip_and_port[0], ip_and_port[1], 'http', anonymity))
        i += 1

    i = 0
    while i < len(socks4_proxies):
        ip_and_port = socks4_proxies[i].split(':')
        anonymity_level = int(socks4_proxy_info[i]['anonymity'])

        if anonymity_level == 3:
            anonymity = 'elite'
        elif anonymity_level == 2:
            anonymity = 'anonymous'
        else:
            anonymity = 'transparent'

        proxies.append(Proxy(ip_and_port[0], ip_and_port[1], 'socks4', anonymity))
        i += 1

    i = 0
    while i < len(socks5_proxies):
        ip_and_port = socks5_proxies[i].split(':')
        anonymity_level = int(socks5_proxy_info[i]['anonymity'])

        if anonymity_level == 3:
            anonymity = 'elite'
        elif anonymity_level == 2:
            anonymity = 'anonymous'
        else:
            anonymity = 'transparent'

        proxies.append(Proxy(ip_and_port[0], ip_and_port[1], 'socks5', anonymity))
        i += 1

    print(f'{get_date_time_str()} - Finished scraping proxies from Proxyscrape')
    return proxies


def scrape_free_proxy_cz() -> list:
    proxies = []

    page_num = 1
    options = Options()
    options.binary = r'/usr/bin/firefox'

    while page_num <= 20:
        driver = webdriver.Firefox(options=options)
        driver.set_page_load_timeout(15)
        driver.get(f'http://free-proxy.cz/en/proxylist/main/{page_num}')
        page_src = driver.page_source
        driver.close()

        try:
            soup = BeautifulSoup(page_src, 'html.parser')
            table = soup.find('table', {'id': 'proxy_list'}).find('tbody')

            for proxy in table.findAll('tr'):
                ip = proxy.findNext('td')
                port = ip.findNext('td')
                protocol = port.findNext('td')
                anonymity = protocol.findNext('td').findNext('td').findNext('td').findNext('td').text

                if anonymity.lower() == 'high anonymity':
                    anonymity = 'elite'

                try:
                    proxies.append(Proxy(ip.text.lower(), port.text.lower(), protocol.text.lower(),
                                         anonymity.lower()))

                except ProxyParametersNullException:
                    pass

            page_num += 1

        except (AttributeError, ProxyParametersNullException):
            page_num += 1
            continue

        except (WebDriverException, TimeoutException):
            break

    print(f'{get_date_time_str()} - Finished scraping proxies from free-proxy.cz')
    return proxies


def scrape_proxies():
    proxies = scrape_free_proxy_cz() + scrape_proxyscrape_proxies() + scrape_free_proxy_list()\
              + scrape_geonode_proxies()

    mysql_ip, mysql_user, mysql_pass = get_database_credentials()
    db = ProxyDatabase(mysql_ip, mysql_user, mysql_pass)

    existing_proxies = db.get_proxies_from_db()

    return filter_duplicate_proxies(proxies, existing_proxies)
