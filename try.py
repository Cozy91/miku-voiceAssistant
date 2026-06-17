import subprocess
import psutil
import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel
import webbrowser
import ollama

model = WhisperModel(
    "small",
    device="cpu"
)

apps = [
    'lutris', 'firefox', 'steam',
    'spotify', 'dolphin', 'sober',
    'libreoffice', 'retroarch'
]

while True:

    duration = 5
    samplerate = 44100

    print("Listening...")

    audio = sd.rec(
        int(duration * samplerate), # ITS CALCULATING TOTAL SAMPLES TAKEN OVER 5 SECS, SAAMPLE RATE IS AMOUNT OF SAMPLES TAKEN IN ONE SECOJD
        samplerate=samplerate,
        channels=1,
        dtype='float32'
    )

    sd.wait()

    sf.write("test.wav", audio, samplerate)

    print("Processing...")

    segments, info = model.transcribe(
        "test.wav",
        beam_size=3 # how strongly the model tries to find the correct text from audio 
    )

    command = ""

    for segment in segments:
        command += segment.text + " "

    command = command.lower().strip()

    print(f"command: {command}")

    responce=ollama.chat( # initializing ollama
             model='qwen3:4b', # llm used, 4 billion parametres
             messages=[
                 {
                     'role':'system',
                     'content':'''
                     you convert speech into commands
                     valid commands:
                     open APP 
                     close APP 
                     search QUERY 
                     return only the command
                     '''
                     },
                 {
                     'role':'user',
                     'content':command
                     }
                 ],
              options={
                  "num_predict":20 #stop after 20 tokens
                  }
                         
            )
    command=responce['message']['content'].lower().strip()
    print(f"llm :{command}")                                            

    if "exit" in command:
        break

    if command.startswith("open "):

        for app in apps:
            if app in command:

                subprocess.Popen([app])
                print(f"opened {app}")

                break

    elif command.startswith("close "):

        for app in apps:
            if app in command:

                for proc in psutil.process_iter(['pid', 'name']):

                    name = proc.info['name']

                    if name and app in name.lower():
                        proc.kill()

                print(f"closed {app}")
                break
    elif command.startswith("search "):
        query=command.replace("search ","")

        webbrowser.open(
                f"https://www.google.com/search?q={query}"
                )
        
        print(f"searched for {query}")  
        
