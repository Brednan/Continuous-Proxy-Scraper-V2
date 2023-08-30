def filter_duplicate_proxies(proxies: list, existing_proxies: list) -> list:
    filtered_proxies = []

    for proxy in proxies:
        is_duplicate = False
        for filtered_proxy in filtered_proxies:
            if proxy.ip == filtered_proxy.ip:
                is_duplicate = True
                break

        for existing_proxy in existing_proxies:
            if proxy.ip == existing_proxy.ip:
                is_duplicate = True
                break

        if not is_duplicate:
            filtered_proxies.append(proxy)

    return filtered_proxies


class ProxyParametersNullException(Exception):
    pass


class Proxy:
    def __init__(self, ip, port, protocol, anonymity_level=None):
        if not ip or not port or not protocol:
            raise ProxyParametersNullException

        self.ip = ip
        self.port = port
        self.protocol = protocol

        if anonymity_level in ('transparent', 'anonymous', 'elite'):
            self.anonymity_level = anonymity_level

        else:
            self.anonymity_level = None

    def __repr__(self):
        return f'{self.ip}:{self.port}'

    def __str__(self):
        return f'{self.ip}:{self.port}'
