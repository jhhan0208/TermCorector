# 모듈 생성하기
import os
import subprocess
from flask import render_template
import time
import math
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from convert_to_mp3 import convert_m4a_to_mp3
from keyword_extraction import keyword
import korean
import pronunciation
from model_txt import preprocess_word_variations, train_model, create_change_bool, change_txt

# 처음 실행 시간 정하기
fir = int(time.time())

folder_path = 'uploads'
convert_m4a_to_mp3(folder_path)
mp3_file = None

for file in os.listdir(folder_path):
    if file.endswith('.mp3'):
        mp3_file = os.path.join(folder_path, file)
        break

from whisper_jax import FlaxWhisperPipline
import jax.numpy as jnp

# pipeline 생성하기
pipeline = FlaxWhisperPipline("openai/whisper-medium", dtype=jnp.float16)

# 변환된 mp3 파일을 분석하여서 결과 추출하기
result = pipeline(mp3_file)

# transcription.txt에 담긴 내용
transcription_text = result["text"] if isinstance(result, dict) and "text" in result else str(result)

# transcription.txt에 대해 raw_text 폴더에 저장하기!
output_dir = "raw_text"
os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(output_dir, "transcription.txt")

with open(output_file, "w", encoding='utf-8') as f:
    f.write(transcription_text)

print(f"Transcription saved to {output_file}")

# 결과 파일 생성
result_dir = "results"
os.makedirs(result_dir, exist_ok=True)

## 데이터 분석
# 1. 키워드 추출

# uploads 폴더에 있는 모든 PDF 파일의 경로를 pdf_paths 리스트에 추가
pdf_paths = [os.path.join('uploads', file) for file in os.listdir('uploads') if file.endswith('.pdf')]

# lst: 추출된 키워드 저장
lst = keyword(pdf_paths)

# 영어 -> 한글 변환 텍스트 + 영어 단어
korean_pron, right_keywords, initial = korean.Korean(lst)

# 발음 데이터 생성
pronunciation.create_df(korean_pron, right_keywords, initial, "word_variations.csv")

# 2. 모델 적용

# whisper 변환 txt 불러오기
# 나중에 "raw_text/transcription.txt"로 변경(지금은 결과 확인 위해 임시)
raw = "raw_text/transcription.txt"
modified = open(raw, 'r', encoding='utf-8').read()

# fasttext를 적용하기 위해 word_variations.csv 가공
sentences, pronunciation_to_target, length, initial = preprocess_word_variations("word_variations.csv")

# 가공된 dataset로 fasttext 모델 학습(추후 grid search 등 더 발전시킬 예정)
fasttext_model = train_model(sentences)

# fasttext가 어떤 단어들을 수정할지 선정하기 위한 bool 배열 선정(추후 구체 방식 도입 예정)
whisper_words, change_spots = create_change_bool(length, initial, 'raw_text/transcription.txt', fasttext_model, pronunciation_to_target)

# 학습된 fasttext로 transcription.txt 파일 직접 수정(웹에서 노란색, 빨간색 표시 위해)
whisper_words = change_txt(length, initial, fasttext_model, whisper_words, change_spots, pronunciation_to_target)
## 데이터 분석

### 저장 전 문장 생성

file_path = "results/result_text.txt"
punctuation_marks = {'.', '?', '!'}
paragraph_count = 1  # Start the paragraph numbering
word_time = 0.556  # Time in seconds per word
start_time = 0  # Starting timestamp in seconds

# 연속된 시간 설정하기
total_words = len(whisper_words)
total_time = round(word_time * total_words)

with open(file_path, "w", encoding="utf-8") as file:
    paragraph = []
    word_count = 0

    for word in whisper_words:
        paragraph.append(word)
        word_count += 1

        # 단어가 지정된 구두점 중 하나로 끝나는지 확인하세요.
        if word[-1] in punctuation_marks and word_count >= 100:
            # 현재 단락의 타임스탬프 계산
            hours = start_time // 3600
            minutes = (start_time % 3600) // 60
            seconds = start_time % 60
            timestamp = f"[{hours:02} : {minutes:02} : {seconds:02}]"

            # 타임스탬프가 포함된 "단락 N" 헤더를 쓴 다음 단락을 작성하세요.
            file.write(f"문장 {paragraph_count} {timestamp}\n")
            file.write(' '.join(paragraph) + '\n\n')
            paragraph_count += 1  # Increment paragraph counter

            # 다음 단락의 시작 시간 업데이트
            start_time += round(word_time * word_count)

            # 다음 단락을 위해서 초기화시키기
            paragraph = []
            word_count = 0

    # 헤더 및 타임스탬프와 함께 마지막 단락에 남은 단어를 작성하세요.
    if paragraph:
        hours = start_time // 3600
        minutes = (start_time % 3600) // 60
        seconds = start_time % 60
        timestamp = f"[{hours:02} : {minutes:02} : {seconds:02}]"

        file.write(f"문장 {paragraph_count} {timestamp}\n")
        file.write(' '.join(paragraph) + '\n\n')

# result_text.txt 생성되었다고 표시
print(f"The file '{file_path}' has been created with the specified content.")

# 끝낸 실행시간을 통해서 시, 분, 초 단위로 계산하여서 얼마 정도 걸렸는지 출력하기
las = int(time.time())
hou = int(0)
miu = int(0)
sec = int(0)
total_sec = las - fir
if total_sec // 3600 >= 1:
    hou = total_sec // 3600
    total_sec = total_sec % 3600
if total_sec // 60 >= 1:
    miu = total_sec // 60
    total_sec = total_sec % 60
sec = total_sec
print(f"It takes {las-fir} seconds. In other words, {hou}HH {miu}MM {sec}SS.")
