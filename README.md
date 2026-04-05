# 🎨 2nd Tech Seminar: OCR & Document AI 실습

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.49.1-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Tesseract](https://img.shields.io/badge/OCR-Tesseract-blue?style=flat-square)
![EasyOCR](https://img.shields.io/badge/OCR-EasyOCR-green?style=flat-square)

이 저장소는 **우리FISA(5기, AI엔지니어링)** 과정의 **2차 기술 세미나**를 위해 준비된 프로젝트입니다. 
다양한 OCR(광학 문자 인식) 라이브러리와 문서 처리 도구들을 비교 분석하고, 이를 시각화하여 확인할 수 있는 도구들을 포함하고 있습니다.

---

## 🚀 주요 기능

### 1. OCR 엔진 통합 및 시각화 (`app.py`)
Streamlit 기반의 웹 애플리케이션을 통해 직관적인 OCR 테스트 환경을 제공합니다.
- **다양한 OCR 엔진**: `Pytesseract`, `EasyOCR`, `Unstructured`를 한곳에서 비교
- **멀티 포맷 지원**: 이미지(`PNG`, `JPG`, `JPEG`) 및 `PDF` 문서 처리
- **영역 시각화**: 인식된 텍스트 영역을 Polygon 바운딩 박스로 이미지 위에 실시간 렌더링
- **추출 전략 비교**: Unstructured의 `hi_res` vs `ocr_only` 전략별 성능/속도 비교

### 2. 단계별 실습 노트북 (`Code/`)
기초부터 심화까지 단계별로 학습할 수 있는 Jupyter Notebook 세트입니다.
- **OCR 기초**: Pytesseract 및 EasyOCR 활용법
- **PDF 마스터**: PyPDF, PyMuPDF를 이용한 텍스트 및 메타데이터 추출
- **문서 파티셔닝**: Unstructured를 활용한 복합 문서(표, 이미지, 텍스트) 분할 및 분석

---

## 📂 프로젝트 구조

```text
.
├── app.py                # Streamlit 메인 애플리케이션
├── requirements.txt      # Python 패키지 의존성
├── packages.txt          # 시스템 패키지 의존성 (Linux/Docker용)
├── Code/                 # 기술별 실습 Jupyter Notebook
│   ├── 01_pytesseract.ipynb
│   ├── 02_EasyOCR.ipynb
│   ├── 03_PyPDF.ipynb
│   ├── 04_PyMuPDF.ipynb
│   └── 05~07_Unstructured_*.ipynb
├── Data/                 # 테스트용 데이터 (이미지, PDF, 샘플 고지서 등)
└── PPT/                  # 세미나 발표 자료 및 관련 이미지
```

---

## 🛠️ 설치 및 실행 방법

### 1. 필수 시스템 패키지 (Prerequisites)
OCR 및 PDF 변환을 위해 아래 도구들이 시스템에 설치되어 있어야 합니다.

#### **Windows**
- **Tesseract OCR**: [설치 페이지](https://github.com/UB-Mannheim/tesseract/wiki)에서 설치 후 환경변수 설정 (한글 데이터 팩 포함 권장)
- **Poppler**: [다운로드](http://blog.alivate.com.au/poppler-windows/) 후 `bin` 폴더를 환경변수 PATH에 추가

#### **Linux (Ubuntu/Debian)**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-kor poppler-utils ffmpeg libsm6 libxext6 libgl1
```

### 2. 가상환경 설정 및 패키지 설치
```bash
# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate

# 의존성 패키지 설치
pip install -r requirements.txt
```

### 3. 애플리케이션 실행
```bash
streamlit run app.py
```

---

## 📝 참고 사항
- **언어 지원**: 현재 기본적으로 한국어(`kor`)와 영어(`eng`)를 지원하도록 설정되어 있습니다.
- **성능 팁**: `Unstructured`의 `hi_res` 전략은 딥러닝 모델을 사용하여 레이아웃 분석이 정교하지만, 처리 속도가 느릴 수 있습니다. 빠른 처리가 필요하면 `ocr_only`를 권장합니다.
- **이미지 경로**: 실습 중 생성된 이미지는 `Code/extracted_images/` 등에 저장될 수 있습니다.

---
Copyright © 2025 Woori FISA 5th AI Engineering. All rights reserved.
