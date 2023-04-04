from pyrogram import Client, filters
import os


app = Client('olyagpt', os.getenv('API_ID'), os.getenv('API_HASH'))


@app.on_message(filters.private)
async def handler(client, message):
    await message.reply("Hi :)")


if __name__ == '__main__':
    app.run()
