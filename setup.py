from setuptools import setup, find_packages

setup(
    name='flatbot',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.7.6',
    install_requires=[
        'lxml',
        'pyyaml',
        'firebase_admin',
        'bcrypt',
        'cryptography',
        'aiohttp',
        'aiohttp_session[secure]',
        'aiohttp_security[session]',
        'aiopg[sa]'
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
