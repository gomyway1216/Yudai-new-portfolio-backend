# The Cloud Functions for Firebase SDK to create Cloud Functions and set up triggers.
from firebase_functions import firestore_fn, https_fn, options

# The Firebase Admin SDK to access Cloud Firestore.
from firebase_admin import initialize_app, firestore
import google.cloud.firestore
import base64
from voice_chat_bot import process_audio
import io
import threading
from pydub import AudioSegment
from pydub.playback import play

app = initialize_app()

@https_fn.on_request()
def addmessage(req: https_fn.Request) -> https_fn.Response:
    """Take the text parameter passed to this HTTP endpoint and insert it into
    a new document in the messages collection."""
    # Grab the text parameter.
    original = req.args.get("text")
    print('original: ', original)
    if original is None:
        return https_fn.Response("No text parameter provided", status=400)

    firestore_client: google.cloud.firestore.Client = firestore.client()

    # Push the new message into Cloud Firestore using the Firebase Admin SDK.
    _, doc_ref = firestore_client.collection("messages").add({"original": original})

    # Send back a message that we've successfully written the message
    return https_fn.Response(f"Message with ID {doc_ref.id} added.")

@firestore_fn.on_document_created(document="messages/{pushId}")
def makeuppercase(event: firestore_fn.Event[firestore_fn.DocumentSnapshot | None]) -> None:
    """Listens for new documents to be added to /messages. If the document has
    an "original" field, creates an "uppercase" field containg the contents of
    "original" in upper case."""
    print('event: ', event)

    # Get the value of "original" if it exists.
    if event.data is None:
        return
    try:
        original = event.data.get("original")
    except KeyError:
        # No "original" field, so do nothing.
        return

    # Set the "uppercase" field.
    print(f"Uppercasing {event.params['pushId']}: {original}")
    upper = original.upper()
    event.data.reference.update({"uppercase": upper})

def play_audio_from_bytes(audio_bytes):
    # Convert bytes data to audio segment
    audio_stream = io.BytesIO(audio_bytes)
    audio_segment = AudioSegment.from_file(audio_stream, format="wav")
    # Play the audio segment
    play(audio_segment)

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

        # audio_thread = threading.Thread(target=play_audio_from_bytes, args=(audio_file,))
        # audio_thread.start()

        if audio_file is None:
            return https_fn.Response("No audio data provided", status=400)

        # Save the audio data to a file
        audio_file.save("input.wav")

        # Process the audio using the process_audio function
        bot_audio_data = process_audio("input.wav")

        if bot_audio_data is None:
            return https_fn.Response("No response generated", status=400)

        # Convert the bot's audio data to base64
        bot_audio_base64 = base64.b64encode(bot_audio_data).decode("utf-8")

        return https_fn.Response(bot_audio_base64, headers={'Content-Type': 'audio/wav'}, status=200)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return https_fn.Response(f"An error occurred: {str(e)}", status=500)