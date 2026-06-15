import subprocess
import psutil
import webbrowser
from faster_whisper import WhisperModel

model_size = "small"

model = WhisperModel(
    model_size,
    device="cpu"
)

segments, info = model.transcribe(
    "/home/cozy/test.wav",
    beam_size=3
)

apps = [
    'lutris', 'firefox', 'steam',
    'spotify', 'dolphin', 'sober',
    'libreoffice', 'retroarch'
]

command = ""

for segment in segments:
    command += segment.text + " "

command = command.lower().strip()

print(f"command: {command}")


if command.startswith("open "):

    for app in apps:
        if app in command:
            subprocess.Popen([app])
            print(f"opened {app}")

            if app == "firefox":
                search = input("what do you want to search: ")

                url = f"https://www.google.com/search?q={search}"

                subprocess.Popen([
                    "firefox",
                    url
                ])

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
