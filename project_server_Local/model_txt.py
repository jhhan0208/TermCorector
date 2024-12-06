import subprocess
import sys

# 패키지 설치 함수 정의
def install_packages(packages):
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# 필요한 패키지 리스트
required_packages = ['gensim', 'jamo', 'konlpy']

# 패키지 설치 실행
install_packages(required_packages)

from gensim.models import FastText
from jamo import h2j, j2hcj
from konlpy.tag import Okt
import pandas as pd

def preprocess_word_variations(path):
    # fasttext 모델 적용 위한 csv 가공
    df = pd.read_csv(path)
    sentences = []
    pronunciation_to_target = {}
    target_to_length = {}
    target_to_initial = {}
    num_of_variations = 80

    for _, row in df.iterrows():
        target_word = row['target']
        pronunciations = row[[f'발음{i+1}' for i in range(num_of_variations)]].dropna().tolist()
        for pronunciation in pronunciations:
            sentences.append([target_word, pronunciation])
            pronunciation_to_target[pronunciation] = target_word
            target_to_length[target_word] = df.loc[df['target'] == target_word, 'length'].values[0]
            target_to_initial[target_word] = df.loc[df['target'] == target_word, 'initial'].values[0]

    return sentences, pronunciation_to_target, target_to_length, target_to_initial

def train_model(sentences):
    fasttext_model = FastText(sentences, vector_size=200, window=3, min_count=1, sg=1, epochs=50)
    return fasttext_model

# 초성 그룹에 대한 매핑
initial_groups = {
    'ㄱ': ['ㄱ', 'ㄲ', 'ㅋ', 'ㅇ', 'ㅎ'],
    'ㄴ': ['ㄴ', 'ㄷ', 'ㄹ', 'ㅁ'],
    'ㄷ': ['ㄷ', 'ㄸ', 'ㅌ', 'ㅅ', 'ㅆ', 'ㄴ', 'ㄹ', 'ㅂ'],
    'ㄹ': ['ㄷ', 'ㄴ', 'ㄹ', 'ㅁ'],
    'ㅁ': ['ㄴ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅍ'],
    'ㅂ': ['ㅂ', 'ㅃ', 'ㅍ', 'ㅁ', 'ㄷ'],
    'ㅅ': ['ㅅ', 'ㅆ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㄷ', 'ㄸ', 'ㅌ'],
    'ㅇ': ['ㄱ', 'ㄲ', 'ㅋ', 'ㅇ', 'ㅎ'],
    'ㅈ': ['ㅅ', 'ㅆ', 'ㅈ', 'ㅉ', 'ㅊ'],
    'ㅊ': ['ㅅ', 'ㅆ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅌ'],
    'ㅋ': ['ㄱ', 'ㄲ', 'ㅋ', 'ㅇ', 'ㅎ', 'ㅌ', 'ㅍ'],
    'ㅌ': ['ㄷ', 'ㄸ', 'ㅌ', 'ㅅ', 'ㅆ', 'ㅋ', 'ㅍ', 'ㅊ'],
    'ㅍ': ['ㅂ', 'ㅃ', 'ㅍ', 'ㅁ', 'ㅋ', 'ㅌ', 'ㅎ'],
    'ㅎ': ['ㄱ', 'ㄲ', 'ㅋ', 'ㅇ', 'ㅎ', 'ㅍ'],
    'ㄲ': ['ㄱ', 'ㄲ', 'ㅋ', 'ㅇ', 'ㅎ'],
    'ㄸ': ['ㄷ', 'ㄸ', 'ㅌ', 'ㅅ', 'ㅆ'],
    'ㅃ': ['ㅂ', 'ㅃ', 'ㅍ', 'ㅁ'],
    'ㅆ': ['ㅅ', 'ㅆ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㄷ', 'ㄸ', 'ㅌ'],
    'ㅉ': ['ㅅ', 'ㅆ', 'ㅈ', 'ㅉ', 'ㅊ']
}

def extract_initial(char):
    temp = h2j(char)
    result = j2hcj(temp)
    return result[0]

# 유사한 target 단어 추출
def get_similar_target_words(target_to_length, target_to_initial, fasttext_model, pronunciation, pronunciation_to_target, top_n=4):
    if pronunciation not in fasttext_model.wv:
        return []

    # 발음과 유사한 다른 발음 찾기
    similar_pronunciations = fasttext_model.wv.most_similar(pronunciation, topn=top_n)

    # 유사 발음에 해당하는 target 단어와의 유사도 점수
    similar_targets_with_scores = []
    seen_targets = set()

    # 텍스트 첫 글자의 초성
    pronunciation_initial = extract_initial(pronunciation[0])

    for similar_pronunciation, similarity_score in similar_pronunciations:
        target = pronunciation_to_target.get(similar_pronunciation)
        if target and target not in seen_targets:
            pronunciation_length = len(pronunciation)
            target_length = target_to_length.get(target)
            target_initial = target_to_initial.get(target)
            if abs(target_length - pronunciation_length) <= 1:
                if pronunciation_initial in initial_groups and target_initial in initial_groups[pronunciation_initial]:
                    similar_targets_with_scores.append((target, round(similarity_score*100, 2)))
                    seen_targets.add(target)

        if len(similar_targets_with_scores) == top_n:
            break

    return similar_targets_with_scores

def create_change_bool(target_to_length, target_to_initial, path, fasttext_model, pronunciation_to_target):
    # Okt를 사용하여 품사 태깅
    okt = Okt()

    # transcription.txt 열기
    with open(path, 'r', encoding='utf-8') as file:
        whisper_words = file.read().split()

    # 수정 여부를 알려줄 bool 배열 선언
    change_spots = [False] * len(whisper_words)

    # 추후 고민을 통해 실제 수정 여부 필터링하는 것으로 대체 필요
    for i, word in enumerate(whisper_words):
        # 품사 태깅
        pos_tagged = okt.pos(word)
        # 명사(Noun), 형용사(Adjective)만
        for word, pos in pos_tagged:
            if pos in ['Noun', 'Adjective']: 
                if get_similar_target_words(target_to_length, target_to_initial, fasttext_model, word, pronunciation_to_target) != [] \
                and get_similar_target_words(target_to_length, target_to_initial, fasttext_model, word, pronunciation_to_target)[0][1] >= 50:
                    change_spots[i] = True

    return whisper_words, change_spots

def change_txt(target_to_length, target_to_initial, fasttext_model, whisper_words, change_spots, pronunciation_to_target):
    
    # 바꿔야 할 단어 수정
    for i, word in enumerate(whisper_words):
        if change_spots[i]:
            temp = get_similar_target_words(target_to_length, target_to_initial, fasttext_model, word, pronunciation_to_target)
            if len(temp) > 0:

                temp_arr = []
                for t in temp:
                    temp_arr.append(t[0])
                temp = temp_arr

                temp_str = ''
                for t in temp:
                    if t is not None:
                        temp_str += t + ', '
                temp = temp_str.rstrip(', ')

                whisper_words[i] = ("[" + str(word) + "->" + str(temp) + "]")

    return whisper_words