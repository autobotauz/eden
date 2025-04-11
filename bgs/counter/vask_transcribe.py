# vosk_transcribe.py
import sys
import wave
from vosk import Model, KaldiRecognizer

model = Model("models/vosk-model-small-en-us-0.15")
wf = wave.open(sys.argv[1], "rb")

if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
    print("Audio file must be WAV format Mono PCM 16kHz")
    sys.exit(1)

rec = KaldiRecognizer(model, wf.getframerate())

result = ""
while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        result += rec.Result()
result += rec.FinalResult()

import json
print(json.loads(result)["text"])
