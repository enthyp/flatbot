#!/usr/bin/env python
from db_connection import get_connection

query = ('DROP TABLE IF EXISTS tracks;'
         'DROP TABLE IF EXISTS users;'
         'DROP TABLE IF EXISTS advertisement;'
         'DROP TABLE IF EXISTS site;')


def main():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            conn.commit()


if __name__ == '__main__':
    main()
