from setuptools import setup, find_packages

setup(
    name="flatbot",
    packages=[
        'api',
        'bot'
    ],
    install_requires=[
        'lxml',
        'pyyaml',
        'firebase_admin',
        'bcrypt',
        'aiohttp',
        'aiohttp_session[secure]'
        'aiohttp_security[session]'
    ],
    entry_points={
        "console_scripts": [
            "flatbot-run=flatbot.__main__:main",
        ]
    },
)
