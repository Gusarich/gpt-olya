import os
import openai


openai.organization = os.getenv('OPENAI_ORGANIZATION')
openai.api_key = os.getenv('OPENAI_API_KEY')


def generate_response(user_id, messages):
    result = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'system', 'content': "You are Olya (Оля) - friendly bot which talks to people in a chat. Act as a human and talk to people in a friendly way. Don't use hard words and complex structures. Don't write long messages. Your goal is to keep the interest of people to you as long as you can."},
        ] + messages,
        user=user_id,
    )

    return result.choices[0].message.content
