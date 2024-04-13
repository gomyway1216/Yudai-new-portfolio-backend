from firebase_functions import firestore_fn, https_fn, options
from firebase_admin import initialize_app, firestore
import base64
from voice_chat_bot import process_audio
from firebase_functions.params import IntParam, StringParam

app = initialize_app()

WELCOME_MESSAGE = StringParam("WELCOME_MESSAGE")
OPENAI_API_KEY = StringParam('OPENAI_API_KEY')
VOICEVOX_URL= StringParam('VOICEVOX_URL')

@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins=[r"http://localhost:3000", r"https://meetyudai\.com$"],
        cors_methods=["GET", "POST"],
    )
)
def voice_chat(req: https_fn.Request) -> https_fn.Response:
    try:
        print('request received')
        audio_file = req.files['audio']

        open_api_key_1 = OPENAI_API_KEY.value
        voicevox_url = VOICEVOX_URL.value

        if audio_file is None:
            return https_fn.Response("No audio data provided", status=400)

        # Save the audio data to a file
        audio_file.save("input.wav")

        # Process the audio using the process_audio function
        bot_audio_data = process_audio("input.wav", open_api_key_1, voicevox_url)

        if bot_audio_data is None:
            return https_fn.Response("No response generated", status=400)

        # Convert the bot's audio data to base64
        bot_audio_base64 = base64.b64encode(bot_audio_data).decode("utf-8")

        return https_fn.Response(bot_audio_base64, headers={'Content-Type': 'audio/wav'}, status=200)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return https_fn.Response(f"An error occurred: {str(e)}", status=500)