import requests
from pydub import AudioSegment
from pydub.playback import play
import io
import threading

# VOICEVOX Engine URL
VOICEVOX_URL = "http://localhost:50021"

def play_audio_from_bytes(audio_bytes):
    # Convert bytes data to audio segment
    audio_stream = io.BytesIO(audio_bytes)
    audio_segment = AudioSegment.from_file(audio_stream, format="wav")
    # Play the audio segment
    play(audio_segment)

def text_to_speech(text):
    # Generate query for speech synthesis
    response = requests.post(
        f"{VOICEVOX_URL}/audio_query",
        params={
            "text": text,
            "speaker": 58,
        },
    )
    audio_query = response.json()

    # Perform speech synthesis
    response = requests.post(
        f"{VOICEVOX_URL}/synthesis",
        headers={
            "Content-Type": "application/json",
        },
        params={
            "speaker": 58,
        },
        json=audio_query,
    )

    # Display error message if status code is not 200
    if response.status_code != 200:
        print("An error occurred. Status code: {}".format(response.status_code))
        print(response.text)
    else:
        # Obtain audio data
        audio = response.content

        # Play the audio data in a separate thread without saving to a file
        audio_thread = threading.Thread(target=play_audio_from_bytes, args=(audio,))
        audio_thread.start()

if __name__ == "__main__":
    # Text to convert to speech
    text = "かつおぶしが好きにゃ。"
    text_to_speech(text)
