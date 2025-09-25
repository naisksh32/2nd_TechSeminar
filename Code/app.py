import numpy as np
import pandas as pd

import streamlit as st
from PIL import Image
import base64

# Head 작성
st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

# 사이드 바 생성
st.sidebar.success("Select a demo above.")

# 메인페이지
# 마크 다운으로 제목 작성
st.title("OCR 진행해보기")

# --- 파일 업로더 ---
uploaded_file = st.file_uploader(
    "파일을 선택하세요.",
    type=['pdf', 'png', 'jpg', 'jpeg', 'pptx', 'ppt', 'docx', 'doc']
)

# --- 업로드된 파일 처리 ---
if uploaded_file is not None:
    # 파일 확장자 확인
    file_extension = uploaded_file.name.split('.')[-1].lower()

    # 이미지 파일 처리
    if file_extension in ['png', 'jpg', 'jpeg']:
        st.subheader("🖼️ 업로드된 이미지")
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption=f"업로드된 이미지: {uploaded_file.name}", use_container_width=True)
        except Exception as e:
            st.error(f"이미지 파일을 여는 중 오류가 발생했습니다: {e}")

    # PDF 파일 처리
    elif file_extension == 'pdf':
        st.subheader("📄 업로드된 PDF")
        try:
            # PDF 파일을 base64로 인코딩하여 iframe으로 표시
            base64_pdf = base64.b64encode(uploaded_file.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"PDF 파일을 처리하는 중 오류가 발생했습니다: {e}")

    # 지원하지 않는 파일 형식 처리
    else:
        st.warning("지원하지 않는 파일 형식입니다. PDF 또는 이미지 파일을 업로드해주세요.")

else:
    st.info("파일을 업로드해주세요.")
