import asyncio
import logging
import os
from datetime import datetime as dt

import firebase_admin
from firebase_admin import messaging


class FirebaseException(Exception):
    pass


class Notifier:
    async def notify(self, channel_id, payload):
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
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        firebase_admin.initialize_app()
        app['notifier'] = Notifier()
    else:
        raise FirebaseException(
            'One must provide credentials path in GOOGLE_APPLICATION_CREDENTIALS environment variable!'
        )
