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
required_packages = ['PyMuPDF', 'konlpy', 'nltk']

# 패키지 설치 실행
install_packages(required_packages)

import re
import fitz
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer

# NLTK 필수 데이터 다운로드
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

# 불용어 리스트 (영어)
stop_words = set(stopwords.words('english'))

# 불용어 추가
additional_stop_words = {
    'kyung', 'hee', 'kyunghee', 'university', 'goal', 'vs', 'eg', 'e.g.', 'e.g', 'ie',
    'i.e.', 'i.e', 'ex', 'etc', 'etc.', 'aka', 'otherwise', 'cf', 'cf.', 'example',
    'yes', 'no', 'thank', 'hw', 'homework', 'ch', 'chapter', 'chap', 'qa', 'lecture',
    'lec', 'youtube'
}

# 불용어 리스트 통합
stop_words = stop_words.union(additional_stop_words)

# 키워드 추출
def keyword(pdf_paths):
    nouns = set()  # 모든 파일의 키워드를 저장할 집합

    lemmatizer = WordNetLemmatizer()  # 단어 원형 추출을 위한 lemmatizer

    # 각 PDF 파일에서 텍스트 추출 및 키워드 처리
    for pdf_path in pdf_paths:
        full_text = []  # 페이지별 전체 텍스트를 저장할 리스트

        # PDF에서 텍스트 추출
        doc = fitz.open(pdf_path)

        for page in doc:
            # 페이지의 텍스트를 가져오기
            page_text = page.get_text()

            # 특수문자, 한글, 링크, 이메일 제거
            page_text = re.sub(r'[■●♦★☆üØ§†‡¶•~™©®€¥£]', '', page_text)
            page_text = re.sub(r'[\u3131-\u3163\uAC00-\uD7A3]+', '', page_text)
            page_text = re.sub(r'\b(?:https?://\S+|www\.\S+)\b', '', page_text)
            page_text = re.sub(r'\S+@khu\.ac\.kr', '', page_text)
            page_text = re.sub(r'[/+(:=]', ' ', page_text)
            page_text = re.sub(r'lec-\d{2}-prg-\d{2}-\S+', '', page_text)
            page_text = re.sub(r'\S+\.py', '', page_text)

            # 줄 단위로 분리하고 문장 결합
            lines = page_text.splitlines()
            current_sentence = ""

            for line in lines:
                if line.strip():
                    if line.strip().endswith('.'):
                        current_sentence += " " + line.strip()
                        full_text.append(current_sentence)  # 완성된 문장 추가
                        current_sentence = ""
                    else:
                        if current_sentence and line[0].islower():
                            current_sentence += " " + line.strip()
                        else:
                            if current_sentence:
                                full_text.append(current_sentence)
                            current_sentence = line.strip()

            if current_sentence:
                full_text.append(current_sentence)

        # 각 문장별로 토큰화 및 품사 태깅 진행
        for sentence in full_text:
            tokens = word_tokenize(sentence)
            tokens = [sub_token for token in tokens for sub_token in re.split(r'[._]', token)]
            tokens = [word for word in tokens if len(word) > 1 and not any(char.isdigit() for char in word)]
            tagged_tokens = pos_tag(tokens)

            for word, pos in tagged_tokens:
                if pos in ('NN', 'NNP', 'JJ'):
                    noun_lemma = lemmatizer.lemmatize(word.lower())
                    nouns.add(noun_lemma)

        doc.close()

    # 하이픈 기준 텍스트 처리
    def handle_hyphen(text):
        parts = text.split('-')
        if parts[0] and parts[-1]:
            if parts[0].isdigit() and parts[-1].isdigit():
                return ''
            else:
                return text
        elif parts[0] and not parts[-1]:
            return '' if parts[0].isdigit() else parts[0] + ''
        elif not parts[0] and parts[-1]:
            return '' if parts[-1].isdigit() else '' + parts[-1]

    # 하이픈 처리 및 1자리 문자 제거
    nouns = [handle_hyphen(word) for word in nouns]
    nouns = [word for word in nouns if len(word) > 1]
    nouns = list(set(nouns))

    # 추출된 단어에서 불용어 제거 후 정렬
    nouns = [word for word in nouns if word not in stop_words]
    nouns = sorted(nouns)

    nouns = [word.replace('-', ' ') for word in nouns]

    return nouns