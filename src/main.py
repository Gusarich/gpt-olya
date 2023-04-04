from pyrogram import Client, filters, enums
import os
import gpt


app = Client('olyagpt', os.getenv('API_ID'), os.getenv('API_HASH'))


def parse_message(msg):
    return {
        'role': 'assistant' if msg.from_user.is_self else 'user',
        'content': msg.text
    }


@app.on_message(filters.private)
async def handler(client, message):
    uid = message.chat.id
    messages = [parse_message(msg) async for msg in app.get_chat_history(uid, 30)][::-1]
    await app.send_chat_action(uid, enums.ChatAction.TYPING)
    try:
        response = gpt.generate_response(str(uid), messages)
        await message.reply(response)
    except:
        await app.send_chat_action(uid, enums.ChatAction.CANCEL)


if __name__ == '__main__':
    app.run()
