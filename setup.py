from setuptools import setup


setup(
    name='sanic_mysql',
    version='0.0.4',
    description='Adds mysql support to sanic .',
    long_description='sanic_mysql is a sanic framework extension which adds support for the mysql.',
    url='https://github.com/jimgreat/sanic_mysql',
    author='jimgreat',
    license='MIT',
    packages=['sanic_mysql'],
    install_requires=('sanic', 'aiomysql'),
    zip_safe=False,
    keywords=['sanic', 'mysql', 'aiomysql'],
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP :: Session',
    ]
)