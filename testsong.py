import pyaudio
from acrcloud.recognizer import ACRCloudRecognizer
import wave
import os

# Your ACRCloud API credentials
config = {
    'host': 'identify-us-west-2.acrcloud.com',
    'access_key': '9e07938d75bbf3805ed9f7760e5c667e',
    'access_secret': 'HncZ3hRNcz8se5Hxsz6qpCvjqSqeP9p6uDD9wbvd',
    'timeout': 10  # seconds
}

def recognize_song():
    """
    Recognizes a song from the microphone using the ACRCloud API.
    """
    try:
        # Initialize PyAudio
        audio = pyaudio.PyAudio()

        # Open microphone stream
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100,
                          input=True, frames_per_buffer=1024)
        frames = []

        print("Listening...")
        for _ in range(0, int(44100 / 1024 * 5)):  # Record for 5 seconds
            data = stream.read(1024)
            frames.append(data)
        print("Finished recording.")

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # Save the recorded data as a temporary WAV file
        temp_wave_file = "temp_audio.wav"
        with wave.open(temp_wave_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(frames))

        # Recognize the song using ACRCloud
        recognizer = ACRCloudRecognizer(config)
        result = recognizer.recognize_by_file(temp_wave_file, 0)
        print(result)

        # Remove the temporary WAV file
        os.remove(temp_wave_file)

    except Exception as e:
        print(f"Error recognizing song: {e}")

if __name__ == '__main__':
    recognize_song()