from sanic.log import log
from aiomysql import create_pool
import os


class SanicMysql:
    def __init__(self, app, mysql_config=None):
        self.app = app
        self.config = mysql_config

        if app:
            self.init_app(app=app)

    async def start(self, _app, loop):
        _k = dict(loop=loop)
        if self.config:
            config = self.config
        else:
            config = _app.config.get('MYSQL')

        _k.update(config)

        _mysql = await create_pool(**_k)
        log.info('opening mysql connection for [pid:{}]'.format(os.getpid()))

        async def _query(sqlstr, args=None):
            async with _mysql.acquire() as conn:
                async with conn.cursor() as cur:
                    final_str = cur.mogrify(sqlstr, args)
                    log.info('mysql query [{}]'.format(final_str))
                    await cur.execute(final_str)
                    value = await cur.fetchall()
                    return value

        async def _execute(sqlstr, args=None):
            async with _mysql.acquire() as conn:
                async with conn.cursor() as cur:
                    final_str = cur.mogrify(sqlstr, args)
                    log.info('mysql query [{}]'.format(final_str))
                    await cur.execute(final_str)
                    await conn.commit()

        setattr(_mysql, 'query', _query)
        setattr(_mysql, 'execute', _execute)

        _app.mysql = _mysql

    def init_app(self, app):

        @app.listener('before_server_start')
        async def aio_mysql_configure(_app, loop):
            await self.start(_app, loop)

        @app.listener('after_server_stop')
        async def close_mysql(_app, loop):
            _app.mysql.close()
            log.info('closing mysql connection for [pid:{}]'.format(os.getpid()))
            await _app.mysql.wait_closed()
