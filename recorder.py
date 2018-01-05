import pyaudio
import threading
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types


class AudioRecorder(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.rate = 16000
        self.chunk = int(self.rate / 10)
        self.content = []
        self.closed = True
        
    def __enter__(self):
        self.audio_interface = pyaudio.PyAudio()
        self.audio_stream = self.audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        return self

    def __exit__(self, type, value, traceback):
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.closed = True
        self.audio_interface.terminate()

    def run(self):
        self.closed = False
        while not self.closed:
            data = self.audio_stream.read(self.chunk)
            self.content.append(data)

    def stop(self):
        self.closed = True
            
    def transcribe(self):
        client = speech.SpeechClient()

        content = b''.join(self.content)
        
        audio = types.RecognitionAudio(content=content)
        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.rate,
            language_code='en-US'
        )

        response = client.recognize(config, audio)

        output = []
        
        for result in response.results:
            text = result.alternatives[0].transcript.strip()
            output.append(text[0].capitalize()+text[1:])
            
        return ". ".join(output)
            
