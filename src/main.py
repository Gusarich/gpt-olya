from pyrogram import Client, filters, enums, raw, errors
import os
import gpt
import asyncio
import sqlite3


app = Client('olyagpt', os.getenv('API_ID'), os.getenv('API_HASH'))
whitelist = [int(i) for i in os.getenv('WHITELIST').split(',')]
con = sqlite3.connect('transcriptions.db')
cur = con.cursor()

cur.execute(f'''CREATE TABLE IF NOT EXISTS Transcriptions (
    text TEXT,
    msg_id INTEGER,
    user_id INTEGER
)''')


def get_transcription(msg, uid):
    cur.execute(
        f'SELECT text FROM Transcriptions WHERE msg_id={msg.id} AND user_id={uid}')
    r = cur.fetchone()
    if r:
        return r[0]
    return None


def add_transcription(msg, uid, text):
    cur.execute(f'''INSERT INTO Transcriptions VALUES (
        "{text}",
        {msg.id},
        {uid}
    )''')
    con.commit()


async def transcribe(msg, uid):
    transcription = get_transcription(msg, uid)
    if transcription is not None:
        return transcription

    while True:
        try:
            result = await app.invoke(
                raw.functions.messages.transcribe_audio.TranscribeAudio(peer=await app.resolve_peer(uid), msg_id=msg.id)
            )
            if not result.pending:
                add_transcription(msg, uid, result.text)
                break
        except errors.BadRequest as e:
            add_transcription(msg, uid, '')
            break
        await asyncio.sleep(5)
    await asyncio.sleep(5)

    return get_transcription(msg, uid)


async def parse_message(msg, uid):
    text = ''
    if msg.voice:
        text = await transcribe(msg, uid)
    elif msg.text:
        text = msg.text

    return {
        'role': 'assistant' if msg.from_user.is_self else 'user',
        'content': text
    }


@app.on_message(filters.private)
async def handler(client, message):
    uid = message.chat.id
    if uid not in whitelist:
        return

    await app.read_chat_history(uid)
    messages = [await parse_message(msg, uid) async for msg in app.get_chat_history(uid, 30)][::-1]
    await app.send_chat_action(uid, enums.ChatAction.TYPING)

    try:
        response = gpt.generate_response(str(uid), messages)
        await message.reply(response)
    except Exception as e:
        print(e)
        await app.send_chat_action(uid, enums.ChatAction.CANCEL)


if __name__ == '__main__':
    app.run()
