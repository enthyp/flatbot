import asyncio
import logging

import firebase_admin
from firebase_admin import messaging


class Notifier:
    @staticmethod
    async def notify(channel_id, payload):
        message = messaging.Message(
            data=payload,
            topic=channel_id
        )

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
           None, lambda: messaging.send(message)
        )
        logging.info('Notified!')


def setup_notifications(app):
    firebase_admin.initialize_app()
    app['notifier'] = Notifier()
