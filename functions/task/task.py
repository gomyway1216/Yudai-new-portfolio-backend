from openai import OpenAI
from text_to_speech import text_to_speech
from speech_to_text import speech_to_text

# Prepare the template
template = """You are an agenet that helps a chunk of text into meaningful task list.
User provide a single text that contains multiple tasks, and you need to extract each task and provide a list of tasks.
Constraints:
- The text will be either in English or Japanese or a mix of both.
"""

def process_audio(audio_file, open_api_key):
    print("running process_audio")

    client = OpenAI(api_key=open_api_key)

    # Initialize messages
    messages = [{"role": "system", "content": template}]

    # Convert speech to text
    user_message = speech_to_text(audio_file, open_api_key)

    # Skip processing if the text is empty
    if user_message == "":
        return None

    print("Your message: \n{}".format(user_message))
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4-turbo",
    )

    bot_message = response.choices[0].message.content
    print("Chatbot's response: \n{}".format(bot_message))

    # return success response
    return bot_message