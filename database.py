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

    def __del__(self):
        self.__connection__.close()

    @staticmethod
    def __get_first_query_value__(cursor: MySQLCursor):
        res = cursor.fetchone()
        cursor.close()

        if res is None:
            return None

        return res[0]

    def __get_proxy_protocol_id__(self, proxy_type: str):
        cursor = self.__connection__.cursor()
        cursor.execute('SELECT type_id FROM proxy_types WHERE proxy_type = %s', (proxy_type,))

        return self.__get_first_query_value__(cursor)

    def __get_proxy_anonymity_id__(self, anonymity: str):
        cursor = self.__connection__.cursor()
        cursor.execute('SELECT anonymity_level_id FROM anonymity_level WHERE anonymity_level = %s', (anonymity,))

        return self.__get_first_query_value__(cursor)

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

        print("Finished scraping proxies!")
        self.__connection__.commit()
