sanic_mysql
==============
Mysql support for sanic.

Built on top of [aiomysql](https://github.com/aio-libs/aiomysql).

install
==============
You can install this package as usual with pip:

```python
pip install sanic-mysql
```

Example

```python
    from sanic import Sanic
    from sanic.response import text
    from sanic_mysql import SanicMysql 
    
    app = Sanic(__name__)
    
    app.config.update(dict(MYSQL=dict(host='127.0.0.1', port=3306,
                           user='root', password='pwd',
                           db='mysql')))
    

    SanicMysql(app)
  
    # or use mysql dsn
    # SanicMysql(app, 
    #   mysql_dsn='mysql://user:pass@localhost:3306/db?charset=utf8mb4')
      
    @app.route("/mysql")
    async def mysq(request):
        val = await request.app.mysql.query('select 10')
        return text(val)
                           
    app.run(host="0.0.0.0", port=8000, debug=True, workers=1)
                           

```

Resources
---------

- [PyPI](https://pypi.python.org/pypi/sanic-mysql)