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
    if not message.text:
        return
    uid = message.chat.id
    await app.read_chat_history(uid)
    messages = [parse_message(msg) async for msg in app.get_chat_history(uid, 30) if msg.text][::-1]
    await app.send_chat_action(uid, enums.ChatAction.TYPING)
    try:
        response = gpt.generate_response(str(uid), messages)
        await message.reply(response)
    except Exception as e:
        print(e)
        await app.send_chat_action(uid, enums.ChatAction.CANCEL)


if __name__ == '__main__':
    app.run()
