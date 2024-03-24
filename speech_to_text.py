import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import threading
import queue
import time
import whisper

fs = 44100  # Sample rate
recording_queue = queue.Queue()
is_recording = False
model = whisper.load_model("base")

def record():
    """Continuously record audio from the microphone."""
    with sd.InputStream(samplerate=fs, channels=1, callback=audio_callback):
        while True:
            if not is_recording:
                time.sleep(0.1)  # Lower CPU usage when not recording

def audio_callback(indata, frames, time, status):
    """This is called for each audio block from the microphone."""
    if is_recording:
        recording_queue.put(indata.copy())

def start_recording():
    global is_recording
    is_recording = True
    print("Recording started. Press Enter to stop.")

def stop_recording_and_save():
    global is_recording
    is_recording = False
    all_chunks = []
    while not recording_queue.empty():
        all_chunks.append(recording_queue.get())
    recording = np.concatenate(all_chunks, axis=0)
    write('input.wav', fs, recording)
    print("Recording stopped and saved.")
    result = model.transcribe('input.wav')
    transcript = result["text"]
    print("Transcription:", transcript)
    return transcript

def speech_to_text():
    input("Press Enter to start recording.\n")
    start_recording()
    input("Recording... Press Enter to stop.\n")
    text = stop_recording_and_save()
    print('text: ', text)
    return text

recording_thread = threading.Thread(target=record, daemon=True)
recording_thread.start()

if __name__ == '__main__':
    while True:
        speech_to_text()