from firebase_admin import messaging


class Notifier:
    def __init__(self, loop, queue):
        self.loop = loop
        self.queue = queue
        self.results = []
        
    async def listen(self):
        while True:
            result = await self.queue.get()
            self.results.append(result)

    async def notify(self):
        topic_name = 'flats'
        payload = self.wrap(self.results)

        if payload:
            message = messaging.Message(
                data=payload,
                topic=topic_name
            )
            
            await self.loop.run_in_executor(
                None, lambda: messaging.send(message) 
            )
             
    @staticmethod
    def wrap(results):
        return {r.name: str(r) for r in results}
