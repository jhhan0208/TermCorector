# subprocess, sys, g2pk ,jamo 모듈 불러오기
import subprocess
import sys
from g2pk import G2p
from jamo import h2j, j2hcj

g2p = G2p()

# char로 h2j, j2hcj의 한글로 초기화시키기
def extract_initial(char):
    temp = h2j(char)
    result = j2hcj(temp)
    return result[0]

# 영어에서 한글로 변환시키기
def get_korean_letter(char):
    mapping = {
        'a': '에이', 'b': '비', 'c': '씨', 'd': '디', 'e': '이', 'f': '에프', 'g': '쥐', 'h': '에이취', 'i': '아이',
        'j': '제이', 'k': '케이', 'l': '엘', 'm': '엠', 'n': '엔', 'o': '오', 'p': '피', 'q': '큐', 'r': '알',
        's': '에스', 't': '티', 'u': '유', 'v': '브이', 'w': '더블유', 'x': '엑스', 'y': '와이', 'z': '즤'
    }
    return mapping.get(char.lower(), char)

# word에서 영어에서 한글로 변환시키기(유사 단어)
def convert_word(word):
    pronunciation = g2p(word)
    
    # 변환되지 않은 영어 단어 예외 처리
    if pronunciation == word:
        if len(word) <= 4:
            letter_pronunciation = ''.join([get_korean_letter(char) for char in word])
            return letter_pronunciation
    return pronunciation

# 맞는 한국어 발음, 키워드 리스트 추출하기
def Korean(words):
    right_korean_pronunciations = []
    right_keywords = []
    initial = []

    for word in words:
        transliterated = convert_word(word)
        
        if transliterated != word:
            right_korean_pronunciations.append(transliterated)
            right_keywords.append(word)
            initial.append(extract_initial(transliterated[0]))
    
    return right_korean_pronunciations, right_keywords, initial
