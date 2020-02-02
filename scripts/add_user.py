#!/usr/bin/env python
import argparse
import bcrypt

from db_connection import get_connection

query = 'INSERT INTO users(login, passwd) VALUES(%s, %s)'


def add_user(login, password):
    with get_connection() as conn:
        with conn.cursor() as cur:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))
            cur.execute(query, (login, hashed))
            conn.commit()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('login', default='user')
    parser.add_argument('password', default='password')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    add_user(args.login, args.password)
