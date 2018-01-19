import os
import re
import logging

from aiomysql import create_pool

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


DNS_PATTERN = r'^\S+://\S+'


class SQLDnsParse(object):
    """ mysql dsn parse"""
    @classmethod
    def parse(cls, dsn):
        if not re.match(DNS_PATTERN, dsn):
            raise ValueError(
                "{dsn} is invalid, only full dsn urls (scheme://host...) "
                "allowed".format(dsn=dsn))

        first_colon = dsn.find(':')
        scheme = dsn[:first_colon].lower()
        if scheme != 'mysql':
            raise ValueError('{scheme} scheme is invalid, using "mysql"')

        dsn_url = dsn[first_colon + 1:]
        url = urlparse.urlparse(dsn_url)

        return dict(
            host=url.hostname,
            db=url.path.split('/')[1],
            password=url.password,
            user=url.username,
            port=url.port,
            charset=urlparse.parse_qs(url.query).get('charset', ['utf8'])[0]
        )


class SanicMysql(object):

    def __init__(self, app, mysql_config=None, mysql_dsn=None):
        self.app = app
        self.config = self.get_mysql_config(mysql_config, mysql_dsn)
        self.log = self.configLog()

        if app:
            self.init_app(app=app)

    def get_mysql_config(self, mysql_config, mysql_dsn):
        if mysql_config:
            return mysql_config
        if mysql_dsn:
            return SQLDnsParse.parse(mysql_dsn)

    def configLog(self):
        logging_format = "[%(asctime)s] %(process)d-%(levelname)s "
        logging_format += "%(module)s::%(funcName)s():l%(lineno)d: "
        logging_format += "%(message)s"

        logging.basicConfig(
            format=logging_format,
            level=logging.DEBUG
        )

        return logging.getLogger()

    async def start(self, _app, loop):
        _k = dict(loop=loop)
        if self.config:
            config = self.config
        else:
            config = _app.config.get('MYSQL')

        _k.update(config)

        _mysql = await create_pool(**_k)
        self.log.info('opening mysql connection for [pid:{}]'.format(os.getpid()))

        async def _query(sqlstr, args=None):
            async with _mysql.acquire() as conn:
                async with conn.cursor() as cur:
                    final_str = cur.mogrify(sqlstr, args)
                    self.log.info('mysql query [{}]'.format(final_str))
                    await cur.execute(final_str)
                    value = await cur.fetchall()
                    return value

        setattr(_mysql, 'query', _query)

        _app.mysql = _mysql

    def init_app(self, app):

        @app.listener('before_server_start')
        async def aio_mysql_configure(_app, loop):
            await self.start(_app, loop)

        @app.listener('after_server_stop')
        async def close_mysql(_app, loop):
            _app.mysql.close()
            self.log.info('closing mysql connection for [pid:{}]'.format(os.getpid()))
            await _app.mysql.wait_closed()
