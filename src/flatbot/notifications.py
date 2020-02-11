import asyncio
import logging

import firebase_admin
from firebase_admin import messaging


class FirebaseException(Exception):
    pass


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


def setup_notifications(app, config):
    if config.google_cred_path:
        firebase_admin.initialize_app()
        app['notifier'] = Notifier()
    else:
        raise FirebaseException(
            'One must provide credentials path in GOOGLE_APPLICATION_CREDENTIALS environment variable!'
        )
