from flatbot.tracking.manager import Manager
from flatbot.tracking.tracker import TrackerFactory


async def cancel_all(app):
    await app['manager'].cancel_tasks()


def setup(app, config):
    factory = TrackerFactory(app['db'], app['notifier'], config)
    tracking_manager = Manager(factory, config)
    app['manager'] = tracking_manager
    app.on_cleanup.append(cancel_all)
