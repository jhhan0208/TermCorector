import os
import subprocess
from flask import render_template
import time
import math

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from keyword_extraction import keyword
import korean
import pronunciation
from model_txt import preprocess_word_variations, train_model, create_change_bool, change_txt

folder_path = 'uploads'
m4a_file = None

for file in os.listdir(folder_path):
    if file.endswith('.m4a'):
        m4a_file = os.path.join(folder_path, file)
        break

import whisper

# tiny, base, small, medium, large 모델 중 선택하여 사용 가능
model = whisper.load_model("medium")

result = model.transcribe(m4a_file, language="Korean")

# Check if the result is a dictionary with a 'text' key
transcription_text = result["text"] if isinstance(result, dict) and "text" in result else str(result)

output_dir = "raw_text"
os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(output_dir, "transcription.txt")

with open(output_file, "w", encoding='utf-8') as f:
    f.write(transcription_text)

print(f"Transcription saved to {output_file}")

output_dir = "results"
os.makedirs(output_dir, exist_ok=True)

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
raw = "raw_text/transcription.txt"
modified = open(raw, 'r', encoding='utf-8').read()

# fasttext를 적용하기 위해 word_variations.csv 가공
sentences, pronunciation_to_target, length, initial = preprocess_word_variations("word_variations.csv")

# 가공된 dataset로 fasttext 모델 학습
fasttext_model = train_model(sentences)

# fasttext가 어떤 단어들을 수정할지 선정하기 위한 bool 배열 선정
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

# Calculate the total time if needed for reference
total_words = len(whisper_words)
total_time = round(word_time * total_words)

with open(file_path, "w", encoding="utf-8") as file:
    paragraph = []
    word_count = 0

    for word in whisper_words:
        paragraph.append(word)
        word_count += 1

        # Check if the word ends with one of the specified punctuation marks
        if word[-1] in punctuation_marks and word_count >= 100:
            # Calculate timestamp for the current paragraph
            hours = start_time // 3600
            minutes = (start_time % 3600) // 60
            seconds = start_time % 60
            timestamp = f"[{hours:02} : {minutes:02} : {seconds:02}]"

            # Write "Paragraph N" header with timestamp, then the paragraph
            file.write(f"문장 {paragraph_count} {timestamp}\n")
            file.write(' '.join(paragraph) + '\n\n')
            paragraph_count += 1  # Increment paragraph counter

            # Update the start time for the next paragraph
            start_time += round(word_time * word_count)

            # Reset for the next paragraph
            paragraph = []
            word_count = 0

    # Write any remaining words in the last paragraph with header and timestamp
    if paragraph:
        hours = start_time // 3600
        minutes = (start_time % 3600) // 60
        seconds = start_time % 60
        timestamp = f"[{hours:02} : {minutes:02} : {seconds:02}]"

        file.write(f"문장 {paragraph_count} {timestamp}\n")
        file.write(' '.join(paragraph) + '\n\n')

###

# result_text.txt 생성되었다고 표시
print(f"The file '{file_path}' has been created with the specified content.")