from openai import OpenAI

def speech_to_text(file_path, api_key_fb):
    # Assuming file_path is a path to the audio file you want to transcribe
    # result = model.transcribe(file_path)
    # transcript = result["text"]
    print("running speech_to_text", file_path)
    with open(file_path, 'rb') as audio_file:
        client = OpenAI(api_key=api_key_fb)
        transcription_result = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
    print("transcription_result:", transcription_result)
    print("Transcription:", transcription_result.text)
    return transcription_result.text