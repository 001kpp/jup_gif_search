from vkwave.bots import SimpleLongPollBot
import aiohttp
import threading
import os
from cache_cleaner import cache_clean
from config import *
from GIF_ex import gif_encs
import vkwave
from ai_utils import GPTClient
import asyncio

GPT = GPTClient(gpt_token, gpt_model, None, assist_id)

async def file_save(url, path) -> str:
     async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content = await response.read()

                with open(path, 'wb') as f:
                        f.write(content)
                return path
threading.Thread(target=cache_clean).start()

async def main():

    bot = SimpleLongPollBot(client=vkwave.client.AIOHTTPClient(loop=asyncio.get_event_loop()), tokens=bot_token, group_id=group_ig)

    @bot.message_handler()
    async def handle(event: bot.SimpleBotEvent) -> str:
        if event.object.object.message.attachments and  event.object.object.message.attachments[0].doc and  event.object.object.message.attachments[0].doc.ext =="gif":
            user_data = (await event.api_ctx.users.get(user_ids=event.object.object.message.from_id)).response[0]
            msg_doc_url =event.object.object.message.attachments[0].doc.url
            paths_to_save = [os.path.join(cache_path, f"{str(user_data.id)}_first.jpg"), 
                            os.path.join(cache_path, f"{str(user_data.id)}_second.jpg"), 
                            os.path.join(cache_path, f"{str(user_data.id)}_final.jpg")] 
            
            gif_encs(await file_save(msg_doc_url, os.path.join(cache_path, f"{str(user_data.id)}_doc.gif")), paths_to_save)
            tr = GPT.create_thread()
            upload_files = [
                            {"type": "image_file", "image_file": {"file_id":GPT.upload_file(paths_to_save[0], purpose="user_data")}}, 
                            {"type": "image_file","image_file":{"file_id":GPT.upload_file(paths_to_save[1], purpose="user_data")}}, 
                            {"type": "image_file", "image_file":{"file_id":GPT.upload_file(paths_to_save[2], purpose="user_data")}},
                        ]
            
            GPT.add_message(tr, upload_files,  img_files=True)
            await event.answer(message= GPT.get_answer(tr)) 
        else:
              await event.answer(message="гифка не найдена")
    asyncio.create_task(bot.run())
    while True: await asyncio.sleep(0)    

asyncio.run(main())