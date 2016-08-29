from setuptools import setup

setup(
    name='depscrape',
    version='0.1',
    py_modules=['depscrape'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        depscrape=depscrape:cli
    ''',
)
