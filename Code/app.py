import streamlit as st
from PIL import Image, ImageDraw
import pytesseract
import easyocr
from unstructured.partition.image import partition_image
from unstructured.partition.pdf import partition_pdf
import io
from pdf2image import convert_from_bytes

# ------------------- OCR 함수 정의 (다각형 좌표 반환 기능 추가) -------------------

# 1. Pytesseract
def ocr_with_pytesseract(image_object):
    """Pytesseract를 사용하여 텍스트와 좌표 추출 (직사각형을 다각형으로 변환)"""
    # image_to_data를 사용하여 상세 정보(좌표 포함) 추출, 출력은 dict 형태로
    try:
        data = pytesseract.image_to_data(image_object, lang='kor+eng', output_type=pytesseract.Output.DICT)
        
        polygons = []
        text_list = []
        n_boxes = len(data['level'])
        for i in range(n_boxes):
            # conf(신뢰도)가 60 이상이고, text가 비어있지 않은 경우에만 처리
            if int(data['conf'][i]) > 60 and data['text'][i].strip() != "":
                (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                # 직사각형 좌표를 4개의 점으로 구성된 다각형으로 변환
                points = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
                polygons.append({'points': points, 'text': data['text'][i]})
                text_list.append(data['text'][i])

        return "\n".join(text_list), polygons
    except Exception as e:
        return f"Pytesseract 오류: {e}", []


# 2. EasyOCR
@st.cache_resource
def get_easyocr_reader():
    return easyocr.Reader(['ko', 'en'])

def ocr_with_easyocr(image_bytes):
    """EasyOCR을 사용하여 텍스트와 다각형 좌표 추출"""
    try:
        reader = get_easyocr_reader()
        result = reader.readtext(image_bytes)
        
        polygons = []
        text_list = []
        for (bbox, text, prob) in result:
            # bbox는 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]] 형태이므로 그대로 사용
            # EasyOCR의 bbox는 이미 4개의 (x,y) 튜플 리스트 형태
            # 주의: EasyOCR의 좌표는 float일 수 있으므로 int로 변환
            points = [(int(p[0]), int(p[1])) for p in bbox] 
            polygons.append({'points': points, 'text': text})
            text_list.append(text)
            
        return "\n".join(text_list), polygons
    except Exception as e:
        return f"EasyOCR 오류: {e}", []

# 3. Unstructured
def ocr_with_unstructured(image_bytes, strategy):
    """Unstructured를 사용하여 텍스트와 다각형 좌표 추출"""
    try:
        img_file = io.BytesIO(image_bytes)
        img_file.name = "temp_image.jpg"
        elements = partition_image(file=img_file, strategy=strategy)
        
        polygons = []
        text_list = []
        for el in elements:
            if hasattr(el.metadata, 'coordinates'):
                coords = el.metadata.coordinates.points
                # Unstructured의 coords는 이미 다각형 형태의 (x,y) 튜플 리스트
                # 주의: Unstructured의 좌표는 float일 수 있으므로 int로 변환
                points = [(int(p[0]), int(p[1])) for p in coords]
                polygons.append({'points': points, 'text': el.text})
                text_list.append(el.text)
        
        return "\n".join(text_list), polygons
    except Exception as e:
        return f"Unstructured 오류: {e}", []


# ------------------- 이미지에 다각형을 그리는 함수 -------------------
def draw_polygons_on_image(image_object, polygons_data):
    """Pillow를 사용하여 이미지에 다각형 바운딩 박스를 그립니다."""
    image_with_polygons = image_object.copy()
    draw = ImageDraw.Draw(image_with_polygons)
    
    for item in polygons_data:
        points = item['points']
        # Pillow의 polygon 함수는 (x1, y1, x2, y2, ...)와 같은 평탄화된 리스트를 받거나,
        # [(x1,y1), (x2,y2), ...]와 같은 튜플 리스트를 받음
        draw.polygon(points, outline="red", width=2)
        
    return image_with_polygons

def draw_polygons_on_pdf(image_object, elements_on_page):
    """
    PIL.Image 객체와 해당 페이지의 Unstructured 요소들을 받아,
    요소 위치에 다각형 바운딩 박스를 그립니다.
    """
    image_with_polygons = image_object.copy().convert("RGB")
    draw = ImageDraw.Draw(image_with_polygons)
    
    for el in elements_on_page:
        # 요소에 좌표 메타데이터가 있는지 확인
        if hasattr(el.metadata, 'coordinates'):
            points = el.metadata.coordinates.points
            # points는 (x1, y1), (x2, y2), ... 형태의 튜플 리스트
            
            # 좌표가 float일 수 있으므로 int로 변환
            int_points = [(int(p[0]), int(p[1])) for p in points]
            
            # 다각형 그리기
            draw.polygon(int_points, outline="red", width=3)
            
    return image_with_polygons

# ------------------- Streamlit 앱 UI -------------------
st.set_page_config(page_title="OCR Tool", page_icon="🎨")
st.title("🎨 OCR 결과 시각화")
st.write("이미지를 업로드하고 OCR을 실행하면, 텍스트와 함께 인식된 영역이 다각형 박스로 표시됩니다.")
st.write("주로 영어가 지원되고, 한국어도 간간히 지원됩니다.")

is_sidebar = False


# --- 메인 화면 ---
uploaded_file = st.file_uploader("추출할 파일을 업로드하세요.", type=["png", "jpg", "jpeg", "pdf"])

if (uploaded_file is not None) and uploaded_file.type in ["image/png", "image/jpg", "image/jpeg"]:
    
	with st.sidebar:
		st.header("⚙️ OCR 설정")
		ocr_engine = st.radio("OCR 엔진 선택", ("Pytesseract", "EasyOCR", "Unstructured"))
		unstructured_strategy = "hi_res"
  
		if ocr_engine == "Unstructured":
			unstructured_strategy = st.radio("Unstructured 전략 선택", ("hi_res", "ocr_only"))
   
		st.info("사이드바에서 원하는 OCR 엔진과 설정을 선택하세요.")

	image_bytes = uploaded_file.getvalue()
	image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

	st.image(image, caption="원본 이미지", use_container_width=True)
	if st.button(f"'{ocr_engine}'(으)로 텍스트 추출 및 시각화 실행", type="primary"):
		extracted_text = ""
		polygons_data = [] # 변수 이름을 boxes_data에서 polygons_data로 변경
		
		with st.spinner(f"{ocr_engine} 엔진으로 OCR을 진행 중입니다..."):
			if ocr_engine == "Pytesseract":
				extracted_text, polygons_data = ocr_with_pytesseract(image)
			elif ocr_engine == "EasyOCR":
				extracted_text, polygons_data = ocr_with_easyocr(image_bytes)
			elif ocr_engine == "Unstructured":
				extracted_text, polygons_data = ocr_with_unstructured(image_bytes, strategy=unstructured_strategy)

		if polygons_data:
			st.subheader("🎨 OCR 결과 시각화")
			# 이미지에 다각형 그리기 함수 호출
			image_with_polygons = draw_polygons_on_image(image, polygons_data)
			st.image(image_with_polygons, caption="인식된 텍스트 영역 (다각형)", use_container_width=True)
			
		st.subheader("✅ 추출된 텍스트")
		st.text_area("결과", extracted_text, height=350)




# --- PDF 파일이 업로드되었을 때만 UI 표시 ---
elif uploaded_file is not None and uploaded_file.type == "application/pdf":
    # --- 사이드바 설정 ---
    with st.sidebar:
        st.header("⚙️ Unstructured 설정")
        # 사용자가 제공한 코드 스니펫에 따라 hi_res와 ocr_only만 제공
        unstructured_strategy = st.radio(
            "분석 전략 선택",
            ("hi_res", "ocr_only"),
            help="""
            - **hi_res**: 고해상도 모델을 사용하여 복잡한 문서(이미지 포함)에서 더 정확한 결과를 얻습니다. (느림)
            - **ocr_only**: 간단한 OCR만 수행하여 텍스트를 빠르게 추출합니다.
            """
        )
    
    # PDF를 바이트로 읽고 이미지로 변환
    pdf_bytes = uploaded_file.getvalue()
    
    try:
        with st.spinner("PDF를 페이지별 이미지로 변환 중..."):
            pdf_images = convert_from_bytes(pdf_bytes)
    except Exception as e:
        st.error(f"PDF를 이미지로 변환하는 데 실패했습니다. 'poppler'가 시스템에 올바르게 설치되었는지 확인하세요.")
        st.error(f"오류 상세: {e}")
        st.stop() # 변환 실패 시 앱 실행 중지

    # --- 메인 화면 ---
    st.subheader("📄 PDF 미리보기 및 페이지 선택")
    page_to_visualize_num = st.selectbox(
        "시각화할 페이지를 선택하세요:",
        range(1, len(pdf_images) + 1)
    )
    
    # 선택된 페이지의 인덱스는 0부터 시작
    selected_page_index = page_to_visualize_num - 1
    selected_page_image = pdf_images[selected_page_index]
    
    st.image(selected_page_image, caption=f"선택된 페이지: {page_to_visualize_num}", use_container_width=True)

    # 분석 실행 버튼
    if st.button(f"'{unstructured_strategy}' 전략으로 PDF 분석 실행", type="primary"):
        
        # 1. 전체 PDF 분석하여 요소 추출
        with st.spinner(f"Unstructured로 전체 PDF 분석 중... (전략: {unstructured_strategy}, 시간이 걸릴 수 있습니다)"):
            try:
                # infer_table_structure=True 옵션은 테이블 구조를 더 잘 인식하게 도와줌
                all_elements = partition_pdf(file=uploaded_file, strategy=unstructured_strategy, infer_table_structure=True)
            except Exception as e:
                st.error("Unstructured 분석 중 오류가 발생했습니다.")
                st.error(f"오류 상세: {e}")
                st.stop()

        # 2. 시각화를 위해 선택된 페이지의 요소들만 필터링
        elements_on_selected_page = [
            el for el in all_elements if el.metadata.page_number == page_to_visualize_num
        ]

        # 3. 시각화 결과 표시
        st.subheader(f"🎨 페이지 {page_to_visualize_num} 요소 시각화")
        if elements_on_selected_page:
            image_with_boxes = draw_polygons_on_pdf(selected_page_image, elements_on_selected_page)
            st.image(image_with_boxes, caption=f"페이지 {page_to_visualize_num}에서 추출된 요소 영역", use_container_width=True)
        else:
            st.warning("선택된 페이지에서 시각화할 요소를 찾지 못했습니다.")

        # 4. 추출된 전체 요소 표시
        st.subheader(f"📝 추출된 전체 요소 목록 (총 {len(all_elements)}개)")
        # st.json을 사용하여 각 요소의 상세 정보를 깔끔하게 표시
        element_details = [
            {
                "page": el.metadata.page_number,
                "type": el.__class__.__name__, # 요소 타입 (e.g., Title, NarrativeText)
                "text": str(el)
            } 
            for el in all_elements
        ]
        st.json(element_details, expanded=False) # expanded=False로 기본적으로 접혀있게 설정


else:
    st.info("먼저 파일을 업로드해주세요.")