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
            msg_text = event.object.object.message.text

            if event.object.object.message.text and ";" in msg_text:
                    msg_text = msg_text.split(";") 
                    print(msg_text)

                    if msg_text[0].isdigit():
                        print(len(msg_text))
                        if(len(msg_text) == 2):
                            print(0,5)
                            if int(msg_text[0]) < 3 or int(msg_text[0]) >10: 
                                await event.answer(message= "количество кадров не должно превышать 10 и должно быть не менее 3")
                                pass
                            else:
                                 msg_text = [msg_text[0], {"type":"text", "text":msg_text[1]}]  
                        elif len(msg_text) > 2:
                             await event.answer(message= "количество аргументов больше 2 (аргументы разделяются знаком ';')")
                             pass 
                    else:
                        print(1)
                        msg_text = {"type":"text", "text":"".join(msg_text)}                        
                        
            print(msg_text)

            msg_doc_url =event.object.object.message.attachments[0].doc.url

            paths_to_save = [] 
            if  isinstance(msg_text, list):
                 k= 0               
                 while k != int(msg_text[0]):
                    paths_to_save.append(os.path.join(cache_path, f"{str(user_data.id)}_{k}.jpg"))
                    k+=1
                    print(k)   
            gif_encs(await file_save(msg_doc_url, os.path.join(cache_path, f"{str(user_data.id)}_doc.gif")), paths_to_save)     

            tr = GPT.create_thread()
      
            upload_files = []
            k=0
            print(len(paths_to_save))
            print(paths_to_save)
            while k != len(paths_to_save):
                 upload_files.append({"type": "image_file", "image_file": {"file_id":GPT.upload_file(paths_to_save[k], purpose="user_data")}})
                 #print(upload_files)
                 k+=1
                 print(k)

            if  isinstance(msg_text, list) and isinstance(msg_text[1], dict): 
                 print(1)
                 upload_files.append(msg_text[1]) 
            elif isinstance(msg_text, dict):
                 print(1)
                 upload_files.append(msg_text) 
            print(upload_files)

            GPT.add_message(tr, upload_files,  img_files=True)
            await event.reply(message= GPT.get_answer(tr)) 
        else:
              pass
        
    asyncio.create_task(bot.run())
    while True: await asyncio.sleep(0)    

asyncio.run(main())