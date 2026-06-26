import re
import subprocesses 
import webbrowser
import psutil
import sounddevice as sd 
import soundfile as sf 
import ollama 
from faster_whisper import WhisperModel 


record_seconds = 5 #duration for which it will listen for audio input(in seconds)
sample_rate=16000 #no of audio samples recorded every second,16kHz for whisper models,16kHz avoids the need to resample internally
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

def record_audio(path: str,seconds: int,samplerate: int)->None:
    """Record 'seconds of mono audio from the default mic and write it to 'path'."""
    print("listening...")
    audio=sd.rec(#start recording 
            int(seconds*samplerate),#total audio samples 
            samplerate=samplerate,
            channels=1, #number of audio channels 
            dtype="float32" #datatype of each audio sample 
            )#recording audio by user
    sd.wait() #waiting untill recording is finished 
    sf.write(path,audio,samplerate)

def transcribe(path:str)->str:
    """run whisper on the recorded WAV file and return the transcribed text."""
    print("transcribing...")
    segments,_info=whisper_model.transcribe(path,beam_size=3)
    text=" ".join(segment.text for segment in segments).strip().lower() # joins all the segments with a spacing  between them 
    return text 

def parse_intent(spoken_text:str)->str:
    """send raw transcibed text to the llm and get back a normalized command string."""
    response=ollama.chat(
            model=llm_model,
            messages=[
                {"role":"system","content":system_prompt},
                {"role":"user","content":spoken_text},
                ],
            options={"num_predict":20}
            )
    raw=response["message"]["content"].lower().strip() #models like the one used here can sometimes respond with <think> tags
    cleaned=re.sub( r"<think>.*?</think>","",raw,flags=re.DOTALL).strip()
    return cleaned 
