import subprocess
import os

files = os.listdir("data/ogg")

if not os.path.exists("data/wav"):
    os.makedirs("data/wav")

for file in files:
    subprocess.call(["ffmpeg", "-i", "data/ogg/" + file, "data/wav/" + file[:-4] + ".wav"])
