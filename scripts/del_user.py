#!/usr/bin/env python
import argparse

from db_connection import get_connection

d_query = 'DELETE FROM users WHERE login = %s'


def delete_user(login):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(d_query, (login,))
            conn.commit()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('login', default='user')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    delete_user(args.login)
