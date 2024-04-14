import requests

def text_to_speech(text, voicevox_url):
    print('text_to_speech triggered with text: ', text)
    # Generate query for speech synthesis
    response = requests.post(
        f"{voicevox_url}/audio_query",
        params={
            "text": text,
            "speaker": 58,
        },
    )
    audio_query = response.json()
    print('audio_query: ', audio_query)

    # Perform speech synthesis
    response = requests.post(
        f"{voicevox_url}/synthesis",
        headers={
            "Content-Type": "application/json",
        },
        params={
            "speaker": 24,
        },
        json=audio_query,
    )

    print('voice vox response: ', response)

    # Display error message if status code is not 200
    if response.status_code != 200:
        print("An error occurred. Status code: {}".format(response.status_code))
        print(response.text)
    else:
        return response.content