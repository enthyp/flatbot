import os
import asyncio
from datetime import datetime as dt


import firebase_admin
from firebase_admin import messaging

class FirebaseException(Exception):
    pass


def setup_firebase():
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        firebase_admin.initialize_app()
    else:
        raise FirebaseException(
            'One must provide credentials path in GOOGLE_APPLICATION_CREDENTIALS environment variable!'
        )


class Notifier:
    async def notify(self, channel_id, updates):
        if updates:
            payload = self.wrap(updates)
            message = messaging.Message(
                data=payload,
                topic=channel_id
            )

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
               None, lambda: messaging.send(message)
            )
            print('Notified!')

    @staticmethod
    def wrap(results):
        return {
            "count": str(len(results)),
            "date": dt.strftime(dt.now(), '%Y:%M:%d %H:%M')
        }
