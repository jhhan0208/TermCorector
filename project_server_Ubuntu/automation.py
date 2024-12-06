import subprocess

# python 실행 함수 정의
# python 코드 실행
def run_script2(python_file_name):
    subprocess.check_call(["python3", f"{python_file_name}.py"])

# 패키지 설치 함수 정의
def pip_install_packages(package):
    try:
        __import__(package)  # 패키지 import를 시도
    except ImportError:
        subprocess.check_call(["pip", "install", package])

# pip 라이브러리 설치 list
pip_list = ["git+https://github.com/sanchit-gandhi/whisper-jax.git", "tiktoken", "numba", "more-itertools", "triton==2.2.0", "Flask", "gensim", "PyMuPDF", "konlpy", "nltk", "g2pk", "jamo", "pandas", "pydub"]


# 가상환경 설정 세팅-(1)(whisper-jax, more-itertools, triton, Flask, gensim, PyMuPDF, konlpy, nltk, g2pk, jamo, pandas, pydub
pip_install_packages(pip_list[0])

# 가상환경 설정 세팅-(2)(tiktoken, numba, more-itertools)
for p in range(1, len(pip_list)):
    pip_install_packages(pip_list[p])

# app.py(flask로 웹으로 띄우기) 실행
run_script2("app")



