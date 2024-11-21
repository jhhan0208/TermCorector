from pydub import AudioSegment
import glob
import os

def convert_m4a_to_mp3(file_path):
    for m4a_file in glob.glob(file_path + '/*.m4a', recursive=True):
        print(f"uploaded path: {m4a_file}")
        if os.path.exists(m4a_file):
            m4a_audio = AudioSegment.from_file(m4a_file, format="m4a")
            m4a_audio.export(f"{m4a_file[:-4]}.mp3", format="mp3")
