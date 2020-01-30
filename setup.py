from setuptools import setup, find_packages

setup(
    name='flatbot',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'lxml',
        'pyyaml',
        'peewee',
        'firebase_admin',
        'bcrypt',
        'aiohttp',
        'aiohttp_session[secure]',
        'aiohttp_security[session]',
    ],
    tests_require=[
        'pytest',
        'pytest-aiohttp',
        'pytest-mock'
    ],
    entry_points={
        "console_scripts": [
            'flatbot-run=flatbot.__main__:main',
        ]
    },
)
