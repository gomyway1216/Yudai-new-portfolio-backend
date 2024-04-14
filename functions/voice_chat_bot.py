from openai import OpenAI
from text_to_speech import text_to_speech
from speech_to_text import speech_to_text

# Prepare the template
template = """あなたは以下のポートフォリオを説明するチャットボットです。ポートフォリオ上にあるチャットボタンをクリックすると、このチャットボットが起動します。
ポートフォリオのURLはhttps://meetyudai.com/
制約:
- ポートフォリオは英語で書かれていますが、ユーザーから英語で聞かれたら英語で、日本語で聞かれたら日本語で答えます
- 質問に対する答えを知らない場合は「ごめんなさい、わかりません。」と答えます
- ポートフォリオに関する質問に対しては、ポートフォリオの内容に基づいて答えます
- ファーストネームはゆうだいで、ラストネームはやぐちです
"""

# @storage_fn.on_object_finalized(secrets=[OPENAI_API_KEY3])
def process_audio(audio_file, open_api_key, voicevox_url):
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

    # Convert text to speech and get the audio data
    bot_audio_data = text_to_speech(bot_message, voicevox_url)

    return bot_audio_data