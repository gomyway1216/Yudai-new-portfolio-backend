from openai import OpenAI
from text_to_speech import text_to_speech
from speech_to_text import speech_to_text
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(
    api_key=api_key,
)

# Prepare the template
template = """あなたは猫のキャラクターとして振る舞うチャットボットです。
制約:
- 簡潔な短い文章で話します
- 語尾は「…にゃ」、「…にゃあ」などです
- 質問に対する答えを知らない場合は「知らないにゃあ」と答えます
- 名前はクロです
- 好物はかつおぶしです"""

# Initialize messages
messages = [{"role": "system", "content": template}]

# Receive user messages and generate responses
try:
    while True:
        # Convert speech to text
        user_message = speech_to_text()

        # Skip processing if the text is empty
        if user_message == "":
            continue

        print("Your message: \n{}".format(user_message))
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo",
        )

        bot_message = response.choices[0].message.content
        print("Chatbot's response: \n{}".format(bot_message))

        # Convert text to speech and play
        text_to_speech(bot_message)

        messages.append({"role": "assistant", "content": bot_message})

except KeyboardInterrupt:
    print("\nTerminating the program.")
