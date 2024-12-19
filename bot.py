from vkwave.bots import SimpleLongPollBot
import aiohttp
import threading
import os
from cache_cleaner import cache_clean
from config import *
from GIF_ex import gif_encs
import vkwave
from ai_utils import GPTClient
from loguru import logger
import asyncio
import sys

logger.remove(0)
logger.add(sys.stderr, level=logger_level, colorize=True, catch=True, backtrace=True)

GPT = GPTClient(gpt_token, gpt_model, None, assist_id)

logger.info(f"main_thread_native_id:{threading.get_native_id()}")

async def file_save(url, path) -> str:
     async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    logger.success(f"succesfull response  code {response.status}")
                    try:
                        with open(path, 'wb') as f:
                                f.write(content)
                        return path
                    except ValueError as e:
                        logger.error(e)
                else:
                        logger.error(f"error response code {response.status}")

cache_clean_tr = threading.Thread(target=cache_clean)
cache_clean_tr.start()
logger.info(f"starting thread: '{cache_clean.__name__}'| thread_id:{cache_clean_tr.native_id}")

async def main():

    bot = SimpleLongPollBot(client=vkwave.client.AIOHTTPClient(loop=asyncio.get_event_loop()), tokens=bot_token, group_id=group_id)

    @bot.message_handler()
    async def handle(event: bot.SimpleBotEvent) -> str:
        peer_id =event.object.object.message.peer_id 
        if int(peer_id) != int(filtered_chat):
            user_data = (await event.api_ctx.users.get(user_ids=event.object.object.message.from_id)).response[0]
            logger.info(f"handled at peer: {peer_id}; user:  {user_data.id}")
            if event.object.object.message.attachments and  event.object.object.message.attachments[0].doc and  event.object.object.message.attachments[0].doc.ext =="gif":
            
                msg_text = event.object.object.message.text
                logger.info(f"object_type in handler 'doc', '.gif' msg_text:{msg_text}")

                if";" in msg_text:
                        msg_text = msg_text.split(";") 
                        logger.debug(f"split msg_text:{msg_text}")

                        if msg_text[0].isdigit():
                            print(len(msg_text))
                            if(len(msg_text) == 2):
                                logger.debug(f"len msg_text: {len(msg_text)}")

                                if int(msg_text[0]) < 3 or int(msg_text[0]) >9: 
                                    await event.answer(message= "количество кадров не должно превышать 9 и должно быть не менее 3")
                                    logger.info(f"bot answer  peer: {peer_id}; user: {user_data.id}; message = 'количество кадров не должно превышать 9 и должно быть не менее 3'")
                                    return None
                                else:
                                    msg_text = [msg_text[0], {"type":"text", "text":msg_text[1]}]  

                            elif len(msg_text) > 2:
                                logger.debug(f"len msg_text: {len(msg_text)}")
                                await event.answer(message= "количество аргументов больше 2 (аргументы разделяются знаком ';')")
                                logger.info(f"bot answer  peer: {peer_id}; user: {user_data.id}; message = 'количество аргументов больше 2 (аргументы разделяются знаком ';''")
                                return None

                        elif msg_text != None or msg_text != '':
                            msg_text = {"type":"text", "text":"".join(msg_text)}                        
                elif str(msg_text):
                    logger.debug(f"msg_text = str")
                    msg_text = {"type":"text", "text":"".join(msg_text)} 

                logger.debug(f"msg_text = {msg_text}")

                msg_doc_url =event.object.object.message.attachments[0].doc.url

                logger.debug(f"msg_doc_url = {msg_doc_url}")

                paths_to_save = [] 
                if  isinstance(msg_text, list): #make save_path  
                    logger.debug("make save path; msg_text is list")
                    i=0
                    try:          
                        while i !=  int(msg_text[0]):
                            paths_to_save.append(os.path.join(cache_path, f"{str(user_data.id)}_{i}.jpg"))
                            i+=1                 
                        gif_encs(path=await file_save(msg_doc_url, os.path.join(cache_path, f"{str(user_data.id)}_doc.gif")), paths_to_save=paths_to_save, frames_to_cut=int(msg_text[0]))                      
                    except ValueError as e:
                        logger.error(e)

                elif isinstance(msg_text, dict) or isinstance(msg_text, str):
                    for i in range(3):
                        paths_to_save.append(os.path.join(cache_path, f"{str(user_data.id)}_{i}.jpg"))
                    gif_encs(path=await file_save(msg_doc_url, os.path.join(cache_path, f"{str(user_data.id)}_doc.gif")), paths_to_save=paths_to_save)
                    
                tr = GPT.create_thread()
        
                upload_files = []

                for i in range(len(paths_to_save)): #add upload_files
                    upload_files.append({"type": "image_file", "image_file": {"file_id":GPT.upload_file(paths_to_save[i], purpose="user_data")}})
                    

                if str(msg_text):
                    if  isinstance(msg_text, list) and isinstance(msg_text[1], dict): 
                        upload_files.append(msg_text[1]) 
                        logger.debug("msg_text append to upload_files")
                    elif isinstance(msg_text, dict):
                        print(msg_text)
                        upload_files.append(msg_text) 
                        logger.debug("msg_text append to upload_files")
                logger.debug(f"upload_files: {upload_files}")    

                GPT.add_message(tr, upload_files,  img_files=True)
                answ_gpt =GPT.get_answer(tr) 
                await event.reply(message=answ_gpt)
                logger.info(f"bot answer  peer: {event.object.object.message.peer_id}; user: {user_data.id}; message = '{answ_gpt}'") 

                GPT.delete_thread(tr)
                logger.success(f"handle_complete at peer: {event.object.object.message.peer_id}; user:  {user_data.id};  object_type: doc, {event.object.object.message.attachments[0].doc.ext}")

            elif event.object.object.message.attachments and  event.object.object.message.attachments[0].doc and  event.object.object.message.attachments[0].doc.ext in ("png", "jpg", "jpeg","bmp"):
                logger.info(f"handled at peer: {event.object.object.message.peer_id}; user:  {user_data.id}")
                msg_doc_url =event.object.object.message.attachments[0].doc.url
                msg_doc_format = event.object.object.message.attachments[0].doc.ext
                msg_text = event.object.object.message.text
                logger.info(f"object_type in handler 'doc', '{msg_doc_format}' msg_text:{msg_text}")

                img =await file_save(msg_doc_url, os.path.join(cache_path, f"{str(user_data.id)}_doc.{msg_doc_format}"))
                
                upload_file = [{"type": "image_file", "image_file": {"file_id":GPT.upload_file(img, purpose="user_data")}}]
                if str(msg_text):
                    msg_text = {"type":"text", "text":"".join(msg_text)} 
                    upload_file.append(msg_text)
                logger.debug(f"msg_text: {msg_text}, upload_file = {upload_file}")
                tr = GPT.create_thread()
                GPT.add_message(tr, upload_file,  img_files=True)
                answ_gpt = GPT.get_answer(tr) 
                await event.reply(message= answ_gpt )
                logger.info(f"bot answer  peer: {peer_id}; user: {user_data.id}; message = '{answ_gpt}'")

                GPT.delete_thread(tr)
                logger.success(f"handle_complete at peer: {peer_id}; user:  {user_data.id}; object_type: doc, {msg_doc_format}")

            elif event.object.object.message.attachments and event.object.object.message.attachments[0].photo:
                logger.info(f"handled at peer: {event.object.object.message.peer_id}; user:  {user_data.id}")
                msg_text = event.object.object.message.text
                logger.info(f"object_type in handler 'photo'; msg_text:{msg_text}")

                photo = await file_save(event.object.object.message.attachments[0].photo.sizes[4].url,  os.path.join(cache_path, f"{str(user_data.id)}_photo.jpg"))
                
                upload_file =[{"type": "image_file", "image_file": {"file_id":GPT.upload_file(photo, purpose="user_data")}}]

                if str(msg_text):
                    msg_text = {"type":"text", "text":"".join(msg_text)} 
                    upload_file.append(msg_text)

                logger.debug(f"msg_text: {msg_text}, upload_file = {upload_file}")  

                tr = GPT.create_thread()
                GPT.add_message(tr, upload_file,  img_files=True) 
                answ_gpt = GPT.get_answer(tr) 

                await event.reply(message= answ_gpt) 
                logger.info(f"bot answer  peer: {peer_id}; user: {user_data.id}; message = '{answ_gpt}'")
                
                GPT.delete_thread(tr)
                logger.success(f"handle_complete at peer: {peer_id}; user:  {user_data.id}; object_type:photo")

                           
    asyncio.create_task(bot.run())
    while True: await asyncio.sleep(0)    

asyncio.run(main())