import os
import sys
import traceback as tb
import yaml

from flatbot.config import DATA_PATH


def get_users():
    # No async because it's only used at the very startup.
    # TODO: real DB introduction should change this, then both users
    # and queries will be stored in DB and accessed async when needed,
    # not kept around in memory all the time.
    pwd_path = os.path.join(DATA_PATH, 'users.yml')

    try:
        with open(pwd_path, 'r') as pwd_file:
            users = yaml.safe_load(pwd_file)
    except Exception: 
        tb.print_exc()
        users = None

    if not users:
        sys.exit(-1)
    else:
        return users


class Storage:
    def __init__(self):
        self.results = {}

    def update(self, id, updates):
        prev = self.results.get(id, [])
        diff = [u for u in updates if u not in prev]

        if diff:
            self.results[id] = updates
        return diff
