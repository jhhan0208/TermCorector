# TermCorector
![image](https://github.com/user-attachments/assets/10951a4f-5d91-4531-a1ee-389c8a21669d)
2024-2학기 캡스톤 디자인으로 진행했던 전공 용어 변환 서비스, "TermCorrector"입니다.

# 프로젝트 소개

- 많은 대학생들은 강의 내용을 녹음해두었다가 STT(speech-to-text) 변환하여 학습에 활용합니다.<br>
- 하지만 기존 STT 서비스는 일상 대화는 변환을 잘 해주지만, 전공 용어는 잘 변환해주지 못합니다.<br>

![image](https://github.com/user-attachments/assets/a14c872a-3cab-414a-8607-4c36a8f3ed13)

<b>이 문제를 해결하기 위해 강의 PDF의 키워드들을 추가적으로 학습하여 전공 용어 인식률을 높이고 학습 활용도를 높이기 위해 프로젝트를 진행하였습니다!</b><br><br>

# ⚙️ 서비스 아키텍처
![image](https://github.com/user-attachments/assets/e7e825ff-2877-4a18-97a6-7625ee2a914e)

# 🔎 핵심 기능 소개
### 1️⃣ 메인 페이지<br>
• 프로젝트 기능 소개<br>
• 사용자가 수강한 강의 녹음 파일, 강의 자료 업로드
![image](https://github.com/user-attachments/assets/b5499b94-2bc8-4c73-9e7e-c441c049b8c1)

### 2️⃣ 로딩/파일 선택 페이지<br>
• STT 변환, fastText 모델 적용 동안 로딩<br>
• 변환한 여러 파일 중 보고 싶은 파일 선택
![image](https://github.com/user-attachments/assets/b2e3b719-148e-4faa-8712-5ffc0d5700e8)

### 3️⃣ 결과 페이지<br>
• fastText 모델이 수정한 단어 직접 확인<br>
• 선택지 중 옳은 단어 선택 및 직접 입력 가능 
![image](https://github.com/user-attachments/assets/d09852ef-f2f7-4102-bfae-dd34c461c3a3)

### 4️⃣ PDF 변환
• 최종 변환 결과를 PDF로 저장<br>
• 웹 뿐만 아니라 로컬 파일로 확인 가능 
![image](https://github.com/user-attachments/assets/e23447b7-f896-421a-aa74-adc837198862)

# ✔️ 결론
• 강의 자료(PDF)에서 전공 용어 키워드를 추출하고, 데이터 증강 기법을 활용하여 전공 용어 변환 오류 수정<br>
• 웹상으로 수정 결과를 직관적으로 확인 가능, 바로 학습에 활용 가능<br>
• 향후, 사용자가 유사한 domain의 여러 강의들을 업로드하여 학습하면, 이전 강의들의 전공 용어들이 모두 DB에 축적되어 전공 용어 변환 정확도 향상을 통해 더욱 유용한 학습 자료로서 활용 가능
