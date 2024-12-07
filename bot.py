from config import *

from vkbottle import PhotoMessageUploader

from vkbottle import API
from vkbottle.bot import Bot, Message

import asyncio

api = API(bot_token)
bot = Bot(api=api)

@bot.on.message(text=["//гифка", "//Гифка", "ЮС гифка", "ЮС Гифка", "юс Гифка", "Юс гифка", "Юс Гифка", "Юс ГИФКА" "юс гифка", "ЮС ГИФКА",  "//ГИФКА"])
async def get_handler(msg: Message):
    users_info = await bot.api.users.get(msg.from_id)
    await msg.answer("{}".format(users_info))

bot.run_forever()
