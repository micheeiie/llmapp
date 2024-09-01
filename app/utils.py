import openai
import os
from dotenv import load_dotenv
from openai import OpenAI
from app.prompt import gpt_system_prompt


load_dotenv()


def generate_answer(query, history, parameters):
    client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY')
    )

    messages = [
        {"role": "system", "content": getattr(gpt_system_prompt, "prompt") },
        {"role": "user", "content": query }
    ]
    # Account for past messages
    history.append(messages)

    # Extract parameters with defaults
    model = parameters.get("model", "gpt-3.5-turbo")
    tokens = parameters.get("max_tokens", 100)
    temp = parameters.get("temperature", 0.7)
    topp = parameters.get("top_p", 1.0)
    freq_penalty = parameters.get("frequency_penalty", 0.0)

    response = client.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages=history,
        max_tokens= tokens,
        temperature= temp,
        top_p= topp,
        frequency_penalty= freq_penalty
    )

    reply = response.choices[0].message.content
    return reply
    