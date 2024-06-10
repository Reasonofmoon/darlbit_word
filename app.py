import streamlit as st
import requests
import pandas as pd
import io
import base64

# Set page configuration with a title and icon
st.set_page_config(
    page_title="Darlbit Word Subsumption with Gemini 1.5 Pro",
    page_icon="📚",
    layout="wide"
)

# Function to call Gemini 1.5 Pro API and fetch processed data
def fetch_processed_data(api_url, api_key, user_input):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'text': user_input
    }
    response = requests.post(api_url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"API 요청 실패: {response.status_code}")
        return None

# Initialize session state for words if not already done
if 'words' not in st.session_state:
    st.session_state.words = []

# User inputs API details
api_url = st.text_input("Gemini 1.5 Pro API URL")
api_key = st.text_input("API Key", type="password")

# Text area for user input
user_input = st.text_area("정리되지 않은 영어 단어 리스트 입력")

if api_url and api_key and user_input:
    processed_data = fetch_processed_data(api_url, api_key, user_input)
    if processed_data:
        st.session_state.words = processed_data
        st.success("입력한 데이터가 성공적으로 전처리되었습니다!")

# Display the words in a table format
def display_words(words):
    df = pd.DataFrame(words)
    st.dataframe(df)

    # Download button for the data
    excel_file = io.BytesIO()
    df.to_excel(excel_file, index=False, sheet_name='Sheet1')
    excel_file.seek(0)
    b64 = base64.b64encode(excel_file.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="processed_words.xlsx">Excel 파일 다운로드</a>'
    st.markdown(href, unsafe_allow_html=True)

display_words(st.session_state.words)

if st.button('모든 단어 삭제'):
    st.session_state.words = []

# Usage instructions
st.markdown("## 앱 사용법")
st.markdown("""
1. Gemini 1.5 Pro API URL과 API Key를 입력합니다.
2. 정리되지 않은 영어 단어 리스트를 텍스트 영역에 입력합니다. 한 줄에 한 단어씩 입력하거나 공백으로 구분하여 여러 단어를 입력할 수 있습니다.
3. 입력한 데이터는 API를 통해 전처리되어 결과가 표시됩니다.
4. '모든 단어 삭제' 버튼을 클릭하여 현재 단어 목록을 삭제할 수 있습니다.
5. 단어 목록 아래의 'Excel 파일 다운로드' 링크를 클릭하여 현재 단어 목록을 Excel 파일로 다운로드할 수 있습니다.
""")

st.warning("중요: 앱을 종료하기 전에 반드시 'Excel 파일 다운로드' 링크를 클릭하여 현재 단어 목록을 저장하십시오. 앱을 종료하면 데이터가 사라질 수 있습니다.")
