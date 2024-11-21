import subprocess

# python-pip 가상환경 설정(AWS)
def pip_activate():
    subprocess.check_call(["source", "whisperenv/bin/activate"])

def conda_activate():
    subprocess.check_call(["conda", "activate", "whisperenv"])

# python 실행 함수 정의
def run_script1(result_file_path, python_name):
    # Run the script only if the file doesn’t exist
    if not os.path.exists(result_file_path):
        subprocess.check_call(["python3", f"{python_name}.py"])

def run_script2(python_file_name):
    subprocess.check_call(["python3", f"{python_file_name}.py"])

# 패키지 설치 함수 정의
def pip_install_packages(package):
    try:
        __import__(package)  # 패키지 import를 시도
    except ImportError:
        subprocess.check_call(["pip", "install", package])

# package pip3 install 함수 정의
def pip3_install_packages(packages):
    for package in packages:
        try:
            __import__(package)  # 패키지 import를 시도
        except ImportError:
            subprocess.check_call(["pip3", "install", package])

# shell로 사전 명령어를 이용해서 하는 함수 정의
def install_setting_sudo(word_list):
    for word in word_list:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call(["sudo", "apt", word])

pip_list = ["git+https://github.com/sanchit-gandhi/whisper-jax.git", "tiktoken", "numba", "more-itertools", "triton==2.2.0", "Flask", "gensim", "PyMuPDF", "konlpy", "nltk", "g2pk", "jamo", "pandas", "pydub"]
#sudo_word_list = ["update", "ffmpeg"]
#pip3_list = ["torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"]

# 가상환경 설정
#pip_activate()
#conda_activate()
pip_install_packages(pip_list[0])

#pip3_install_packages(pip3_list[0])
for p in range(1, len(pip_list)):
    pip_install_packages(pip_list[p])
#run_script2("app")
run_script2("app_jax")


