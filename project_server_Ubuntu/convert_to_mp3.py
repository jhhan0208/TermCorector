from pydub import AudioSegment
import glob
import os

# m4a.파일 확장자에서 mp3 파일 확장자로 변환 파일 생성
def convert_m4a_to_mp3(file_path):
    # m4a_file이 있는 파일 이름 리스트를 다 탐색하기
    for m4a_file in glob.glob(file_path + '/*.m4a', recursive=True):
        # m4a file 경로를 업로드
        print(f"uploaded path: {m4a_file}")
        # m4a file 경로가 있을 때 확장자 .m4a에서 .mp3로 변환하기
        if os.path.exists(m4a_file):
            m4a_audio = AudioSegment.from_file(m4a_file, format="m4a")
            m4a_audio.export(f"{m4a_file[:-4]}.mp3", format="mp3")

