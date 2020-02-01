from flatbot.bot.manager import Manager
from flatbot.bot.notifications import Notifier


async def cancel_all(app):
    await app['manager'].cancel_tasks()


def setup(app, db, config):
    notifier = Notifier()
    manager = Manager(db, notifier, config)
    app['manager'] = manager
    app.on_cleanup.append(cancel_all)
