import subprocess
import sys
from g2pk import G2p
from jamo import h2j, j2hcj

# Initialize the g2pk engine
g2p = G2p()

def extract_initial(char):
    temp = h2j(char)
    result = j2hcj(temp)
    return result[0]

def get_korean_letter(char):
    mapping = {
        'a': '에이', 'b': '비', 'c': '씨', 'd': '디', 'e': '이', 'f': '에프', 'g': '쥐', 'h': '에이취', 'i': '아이',
        'j': '제이', 'k': '케이', 'l': '엘', 'm': '엠', 'n': '엔', 'o': '오', 'p': '피', 'q': '큐', 'r': '알',
        's': '에스', 't': '티', 'u': '유', 'v': '브이', 'w': '더블유', 'x': '엑스', 'y': '와이', 'z': '즤'
    }
    return mapping.get(char.lower(), char)

def convert_word(word):
    pronunciation = g2p(word)
    
    # 영어 단어 그대로 나오는 경우 예외 처리 - 변환이 되지 않은 단어들을 보면 대부분이 약어임.
    if pronunciation == word:
        # 영어 약어의 경우 일반적으로 3~4자인 것에 기반하여 4자 이하인 단어들에 대해서만 진행
        if len(word) <= 4:
            letter_pronunciation = ''.join([get_korean_letter(char) for char in word])
            return letter_pronunciation
    return pronunciation

def Korean(words):
    right_korean_pronunciations = []
    right_keywords = []
    initial = []

    # Process each word and convert its pronunciation
    for word in words:
        transliterated = convert_word(word)
        
        # If the word has been successfully transliterated, add it to the list
        if transliterated != word:  # It means the word was changed
            right_korean_pronunciations.append(transliterated)
            right_keywords.append(word)
            initial.append(extract_initial(transliterated[0]))
    
    return right_korean_pronunciations, right_keywords, initial
