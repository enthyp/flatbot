#!/usr/bin/env python 
import sys
import os
import bcrypt
import yaml

root_path = os.path.dirname(os.path.abspath(__file__))
pwd_path = os.path.join(root_path, '..', 'data', 'pwd.yml')


def add_user(login, password):
    try:
        with open(pwd_path, 'r') as pwd_file:
            users = yaml.safe_load(pwd_file)
    except Exception:
        users = None

    if not users:
        users = {}

    login, password = sys.argv[1], sys.argv[2]
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))
    users.update({login: hashed.decode()})

    with open(pwd_path, 'w') as pwd_file:
        yaml.safe_dump(users, pwd_file)

if __name__ == '__main__':
    assert len(sys.argv) == 3
    add_user(*sys.argv[1:])

