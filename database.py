import mysql.connector.errors
from mysql import connector
from mysql.connector.cursor import MySQLCursor
from proxy import Proxy


class ProxyDatabase:
    def __init__(self, host: str, username: str, password: str):
        self.__connection__ = connector.connect(host=host,
                                                user=username,
                                                password=password,
                                                database='scraped_proxies')

        self.__protocols = self.__get_protocols__()
        self.__anonymity_levels = self.__get_anonymity_levels__()

    def __del__(self):
        self.__connection__.close()

    @staticmethod
    def __get_first_query_value__(cursor: MySQLCursor):
        res = cursor.fetchone()
        cursor.close()

        if res is None or len(res) < 1:
            return None

        return res[0]

    def __get_proxy_protocol_id__(self, proxy_type: str) -> int:
        for p_type in self.__protocols:
            if p_type[1] == proxy_type:
                return p_type[0]

        return 0

    def __get_proxy_anonymity_id__(self, anonymity: str):
        for p_type in self.__anonymity_levels:
            if p_type[1] == anonymity:
                return p_type[0]

        return 0

    def __get_anonymity_level_by_id__(self, anonymity_id: int):
        for a in self.__anonymity_levels:
            if anonymity_id == a[0]:
                return a[1]

    def __get_protocol_by_id__(self, protocol_id: int):
        for a in self.__protocols:
            if protocol_id == a[0]:
                return a[1]

    def __get_protocols__(self):
        cursor = self.__connection__.cursor()
        cursor.execute('SELECT type_id, proxy_type FROM proxy_types')

        res = cursor.fetchall()
        cursor.close()

        return res

    def __get_anonymity_levels__(self):
        cursor = self.__connection__.cursor()
        cursor.execute('SELECT anonymity_level_id, anonymity_level FROM anonymity_level')

        res = cursor.fetchall()
        cursor.close()

        return res

    def __reset_auto_increment(self, table_name):
        cursor = self.__connection__.cursor()
        cursor.execute(f'ALTER TABLE {table_name} AUTO_INCREMENT = 1')
        cursor.close()

    def add_proxy(self, proxy: Proxy):
        protocol_id = self.__get_proxy_protocol_id__(proxy.protocol)
        anonymity_id = self.__get_proxy_anonymity_id__(proxy.anonymity_level)

        if anonymity_id is not None:
            sql_statement = 'INSERT INTO proxies (ip, port, proxy_type_id, anonymity_id) VALUES (%s, %s, %s, %s)'
            cursor = self.__connection__.cursor()
            cursor.execute(sql_statement, (proxy.ip, proxy.port, protocol_id, anonymity_id))

        else:
            sql_statement = 'INSERT INTO proxies (ip, port, proxy_type_id) VALUES (%s, %s, %s)'
            cursor = self.__connection__.cursor()
            cursor.execute(sql_statement, (proxy.ip, proxy.port, protocol_id))

        cursor.close()

    def add_proxies(self, proxies: list):
        for proxy in proxies:
            try:
                self.add_proxy(proxy)
            except mysql.connector.errors.IntegrityError:
                self.__reset_auto_increment('proxies')
                continue

        self.__connection__.commit()

    def get_proxies_from_db(self, protocol=None, anonymity_level=None) -> list:
        cursor = self.__connection__.cursor()

        if protocol is None and anonymity_level is None:
            cursor.execute('SELECT ip, port, proxy_type_id, anonymity_id FROM proxies')

        elif anonymity_level is None:
            protocol_id = self.__get_proxy_protocol_id__(protocol)

            if protocol_id is not None:
                cursor.execute('SELECT ip, port, proxy_type_id, anonymity_id FROM proxies WHERE proxy_type_id = %s',
                               (protocol_id,))
            else:
                return []

        elif protocol is None:
            anonymity_level_id = self.__get_proxy_anonymity_id__(anonymity_level)

            if anonymity_level_id is not None:
                cursor.execute('SELECT ip, port, proxy_type_id, anonymity_id FROM proxies WHERE proxy_type_id = %s',
                               (anonymity_level_id,))
            else:
                return []

        proxies = []
        res = cursor.fetchall()
        cursor.close()
        for p in res:
            anonymity = self.__get_anonymity_level_by_id__(p[3])
            protocol = self.__get_protocol_by_id__(p[2])
            proxies.append(Proxy(p[0], p[1], protocol, anonymity))

        return proxies
