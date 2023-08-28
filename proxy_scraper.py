import requests
from bs4 import BeautifulSoup
from proxy import Proxy, filter_duplicate_proxies
from utilities import get_date_time_str, get_database_credentials
from database import ProxyDatabase


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

        data = requests.get(f'https://proxylist.geonode.com/api/proxy-list?limit=500&page={page_num}&sort_by=lastChecke'
                            f'd&sort_type=desc', headers=headers)
        if not data.json():
            break

        proxy_list = data.json().get('data')

        if not proxy_list or len(proxy_list) <= 0:
            break

        for item in proxy_list:
            proxies.append(Proxy(item['ip'], item['port'], item['protocols'][0], item['anonymityLevel']))

        page_num += 1

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


def scrape_proxies():
    proxies = scrape_geonode_proxies() + scrape_free_proxy_list() + scrape_proxyscrape_proxies()

    mysql_ip, mysql_user, mysql_pass =  get_database_credentials()
    db = ProxyDatabase(mysql_ip, mysql_user, mysql_pass)

    existing_proxies = db.get_proxies_from_db()

    return filter_duplicate_proxies(proxies + existing_proxies)
