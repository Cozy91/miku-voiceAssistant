import re
import subprocesses 
import webbrowser
import psutil
import sounddevice as sd 
import soundfile as sf 
import ollama 
from faster_whisper import WhisperModel 


record_seconds = 5 #duration for which it will listen for audio input(in seconds)
sample_rate=16000 #no of audio samples recorded every second,16kHz for whisper models
audio_file="command.wav" #audio will be saved here 

whisper_model_size="small"
llm_model="qwen3:4b" 

APP=[
        "firefox","spotify","steam","lutris",
        "dolphin","libreoffice","retroarch",
        ]
#instructions given to the llm for every request. this basically does all this every time user gives a prompt
system_prompt="""You convert a spoken sentence into exactly one command. 
valid commands(return ONLY one of these,nothing else):
    open APP
    close APP
    search QUERY
    exit 
rules:
    -APP must be one of "firefox","spotify","steam","lutris",
        "dolphin","libreoffice","retroarch"
    -do not explain. Do not add punctuation.
    -if the sentence does not match any command,return:unknown
"""

print(f"loading Whisper model '{whisper_model_size}")
model=WhisperModel(whisper_model_size,device="cuda",compute_type="int8") #running on gpu with int 8
print("\n Ready")



