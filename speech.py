import torch
from TTS.api import TTS
from sys import argv
import codecs

largv=len(argv)
text_bot_m=''
for i in range(1, largv):
    text_bot_m+=argv[i]+' '


fileObj = codecs.open("C:\\Users\\becke\\OneDrive\\Документы\\resp.txt", "r", "utf_8_sig" )
text_bot_m = fileObj.read()
fileObj.close()
print(text_bot_m)

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# List available 🐸TTS models
print(TTS().list_models())

# Init TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

# Run TTS
# ❗ Since this model is multi-lingual voice cloning model, we must set the target speaker_wav and language
# Text to speech list of amplitude values as output
# wav = tts.tts(text="Hello world!", speaker_wav="audio.ogg", language="en")
# Text to speech to a file
# tts.tts_to_file(text=text_bot_m, speaker_wav="C:\\Users\\becke\\OneDrive\\Desktop\\bot\\audio.ogg", 
#     language="ru", file_path="C:\\Users\\becke\\OneDrive\\Desktop\\bot\\voice.wav")"C:\Users\becke\Downloads\RAM Bakasura.mp3"
# tts.tts_to_file(text=text_bot_m, speaker_wav="C:\\Users\\becke\\OneDrive\\Desktop\\bot\\aggressive", 
#     language="ru", file_path="C:\\Users\\becke\\OneDrive\\Desktop\\bot\\voice.wav")
tts.tts_to_file(text=text_bot_m, speaker_wav="C:\\Users\\becke\\OneDrive\\Desktop\\bot\\putin", 
    language="ru", file_path="C:\\Users\\becke\\OneDrive\\Desktop\\bot\\voice.wav")


f = open("C:\\Users\\becke\\OneDrive\\Desktop\\bot\\check.txt", "w")
f.write("ok")
f.close()