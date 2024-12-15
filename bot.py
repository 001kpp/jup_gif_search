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

    bot = SimpleLongPollBot(client=vkwave.client.AIOHTTPClient(loop=asyncio.get_event_loop()), tokens=bot_token, group_id=group_id)

    @bot.message_handler()
    async def handle(event: bot.SimpleBotEvent) -> str:
        if int(event.object.object.message.peer_id) != int(filtered_chat):
            user_data = (await event.api_ctx.users.get(user_ids=event.object.object.message.from_id)).response[0]
            if event.object.object.message.attachments and  event.object.object.message.attachments[0].doc and  event.object.object.message.attachments[0].doc.ext =="gif":
                msg_text = event.object.object.message.text
                if";" in msg_text:
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
                        elif msg_text != None or msg_text != '':
                            print(10)
                            msg_text = {"type":"text", "text":"".join(msg_text)}                        
                elif str(msg_text):
                    print(11)
                    msg_text = {"type":"text", "text":"".join(msg_text)}                    
                print(msg_text)

                msg_doc_url =event.object.object.message.attachments[0].doc.url

                paths_to_save = [] 
                if  isinstance(msg_text, list): #make save_path  
                    i=0          
                    while i !=  int(msg_text[0]):
                        paths_to_save.append(os.path.join(cache_path, f"{str(user_data.id)}_{i}.jpg"))
                        i+=1
                        print(i)   
                    gif_encs(path=await file_save(msg_doc_url, os.path.join(cache_path, f"{str(user_data.id)}_doc.gif")), paths_to_save=paths_to_save, frames_to_cut=int(msg_text[0]))     
                elif isinstance(msg_text, dict) or isinstance(msg_text, str):
                    for i in range(3):
                        paths_to_save.append(os.path.join(cache_path, f"{str(user_data.id)}_{i}.jpg"))
                        print(paths_to_save)
                    gif_encs(path=await file_save(msg_doc_url, os.path.join(cache_path, f"{str(user_data.id)}_doc.gif")), paths_to_save=paths_to_save)
                    
                tr = GPT.create_thread()
        
                upload_files = []

                for i in range(len(paths_to_save)): #add upload_files
                    upload_files.append({"type": "image_file", "image_file": {"file_id":GPT.upload_file(paths_to_save[i], purpose="user_data")}})
                    print("76str ", upload_files)
                print(msg_text)
                if str(msg_text):
                    if  isinstance(msg_text, list) and isinstance(msg_text[1], dict): 
                        print(2)
                        upload_files.append(msg_text[1]) 
                    elif isinstance(msg_text, dict):
                        print(msg_text)
                        upload_files.append(msg_text) 
                    print("84str ", upload_files)

                GPT.add_message(tr, upload_files,  img_files=True)
                await event.reply(message= GPT.get_answer(tr)) 
                GPT.delete_thread(tr)

            elif event.object.object.message.attachments and  event.object.object.message.attachments[0].doc and  event.object.object.message.attachments[0].doc.ext in ("png", "jpg", "jpeg","bmp"):
                msg_doc_url =event.object.object.message.attachments[0].doc.url
                msg_doc_format = event.object.object.message.attachments[0].doc.ext
                msg_text = event.object.object.message.text

                img =await file_save(msg_doc_url, os.path.join(cache_path, f"{str(user_data.id)}_doc.{msg_doc_format}"))
                print("55 ",img)
                upload_file = [{"type": "image_file", "image_file": {"file_id":GPT.upload_file(img, purpose="user_data")}}]
                if str(msg_text):
                    msg_text = {"type":"text", "text":"".join(msg_text)} 
                    upload_file.append(msg_text)
                tr = GPT.create_thread()
                GPT.add_message(tr, upload_file,  img_files=True)  
                await event.reply(message= GPT.get_answer(tr)) 
                GPT.delete_thread(tr)

            elif event.object.object.message.attachments and event.object.object.message.attachment[0].photo:
                photo = await file_save(event.object.object.message.attachments[0].photo.sizes[4].url, f"{str(user_data.id)}_photo.jpg")
                upload_file =[{"type": "image_file", "image_file": {"file_id":GPT.upload_file(photo, purpose="user_data")}}]
                msg_text = event.object.object.message.text
                if str(msg_text):
                    msg_text = {"type":"text", "text":"".join(msg_text)} 
                    upload_file.append(msg_text)
                tr = GPT.create_thread()
                GPT.add_message(tr, upload_file,  img_files=True)  
                await event.reply(message= GPT.get_answer(tr)) 
                GPT.delete_thread(tr)

                 
            
    asyncio.create_task(bot.run())
    while True: await asyncio.sleep(0)    

asyncio.run(main())