#!/usr/bin/env python
from conn import get_connection


drop_all_query = (
    'DROP TABLE IF EXISTS tracks;'
    'DROP TABLE IF EXISTS users;'
    'DROP TABLE IF EXISTS advertisement;'
    'DROP TABLE IF EXISTS site;')

user_query = ('CREATE TABLE IF NOT EXISTS users('
              'id SERIAL PRIMARY KEY, '
              'login VARCHAR (100) UNIQUE NOT NULL, '
              'passwd VARCHAR (500) NOT NULL);')

site_query = ('CREATE TABLE IF NOT EXISTS site('
              'id SERIAL PRIMARY KEY, '
              'url VARCHAR (200) UNIQUE NOT NULL);')

advertisement_query = ('CREATE TABLE IF NOT EXISTS advertisement('
                       'id SERIAL PRIMARY KEY, '
                       'url VARCHAR (200) UNIQUE NOT NULL, '
                       'content VARCHAR (500) NOT NULL, '
                       'site_id SERIAL NOT NULL REFERENCES site(id) ON DELETE CASCADE);')

tracks_query = ('CREATE TABLE IF NOT EXISTS tracks('
                'user_id SERIAL REFERENCES users(id) ON DELETE CASCADE, '
                'site_id SERIAL REFERENCES site(id) ON DELETE CASCADE, '
                'CONSTRAINT tracks_pk PRIMARY KEY (user_id, site_id));')


def main():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(drop_all_query)
            cur.execute(user_query)
            cur.execute(site_query)
            cur.execute(advertisement_query)
            cur.execute(tracks_query)

            conn.commit()


if __name__ == '__main__':
    main()
