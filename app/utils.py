# from bson.objectid import ObjectId
# from .database import conversations_collection, conversation_helper
# from .schemas import ConversationPOST, ConversationPUT

import openai
import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


# def create_conversation(conversation_data: ConversationPOST) -> dict:
#     return None

# def get_conversations() -> list:
#     return None

# def get_conversation(id: str) -> dict:
#     return None

# def update_conversation(id: str, conversation_data: ConversationPUT):
#     return None

# def delete_conversation(id: str):
#     return True

def generate_answer(query):
    client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY')
    )

    messages = [
        {"role":"system",
         "content": "You are a helpful assistant."}
    ]
    messages.append(
        {"role": "user",
         "content": f'{query}'}
    )
    response = client.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages=messages
    )
    reply = response.choices[0].message.content
    return reply
