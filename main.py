from pyrogram.types import Message
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent

from web import keep_alive
keep_alive()

#Pyrogram connection specifications
api_id = 25444013
api_hash = "bfbb5734526653271b8a106d046b5754"
bot_token = "6022537053:AAHJCv2FJRQCYKPIvokoPoM6fYKQV7JYvvE"

admin = 5861650867
app = Client("bot", api_id, api_hash, bot_token=bot_token)

@app.on_message(filters.command("start"))
async def amo(bot,message):
    await app.send_message(message.chat.id,"hi")



@app.on_message()
async def download_duc(bot,message):
    await app.send_message(message.chat.id,"downloading . . .")
    await app.download_media(message)
    await app.send_message(message.chat.id,"downloaded")


app.run()
