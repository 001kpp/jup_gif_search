from vkwave.bots import SimpleLongPollBot
from config import *
import vkwave
import asyncio

async def main():
    bot = SimpleLongPollBot(client=vkwave.client.AIOHTTPClient(loop=asyncio.get_event_loop()), tokens=bot_token, group_id=group_ig)
    @bot.message_handler(bot.text_filter("начало"))
    async def handle(event: bot.SimpleBotEvent) -> str:
        user_data = (await event.api_ctx.users.get(user_ids=event.object.object.message.from_id)).response[0]
        await event.answer(message=user_data) 
    asyncio.create_task(bot.run())
    while True: await asyncio.sleep(0)    

asyncio.run(main())