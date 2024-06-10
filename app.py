import streamlit as st
import pandas as pd
import re
from PyDictionary import PyDictionary
import io
import base64

# Set page configuration with a title and icon
st.set_page_config(
    page_title="Darlbit Word Subsumption",
    page_icon="📚",
    layout="wide"
)

# Function to fetch word details from PyDictionary
def fetch_word_details(word):
    dictionary = PyDictionary()
    try:
        meanings = dictionary.meaning(word)
        if meanings:
            definition = ' '.join(meanings[list(meanings.keys())[0]])
        else:
            definition = "Definition not found"
    except:
        definition = "Definition not found"

    try:
        synonyms = ', '.join(dictionary.synonym(word))
        if not synonyms:
            synonyms = "Not found"
    except:
        synonyms = "Not found"

    try:
        antonyms = ', '.join(dictionary.antonym(word))
        if not antonyms:
            antonyms = "Not found"
    except:
        antonyms = "Not found"

    return definition, synonyms, antonyms

# Initialize session state for words if not already done
if 'words' not in st.session_state:
    st.session_state.words = []

# Text area for user input
user_input = st.text_area("정리되지 않은 영어 단어 리스트 입력")

if user_input:
    # Extract words from the user input
    words = re.findall(r'\b\w+\b', user_input)

    # Fetch details for each word
    data = []
    for new_word in words:
        if new_word:
            definition, synonyms, antonyms = fetch_word_details(new_word)
            new_word_entry = {
                "단어": new_word,
                "의미": definition,
                "동의어": synonyms,
                "반의어": antonyms
            }
            data.append(new_word_entry)

    st.session_state.words.extend(data)
    st.success("입력한 단어 리스트가 성공적으로 추가되었습니다!")

# Display the words in a table format
def display_words(words):
    df = pd.DataFrame(words)
    st.dataframe(df)

    # Download button for the data
    excel_file = io.BytesIO()
    df.to_excel(excel_file, index=False, sheet_name='Sheet1')
    excel_file.seek(0)
    b64 = base64.b64encode(excel_file.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="words.xlsx">Excel 파일 다운로드</a>'
    st.markdown(href, unsafe_allow_html=True)

display_words(st.session_state.words)

if st.button('모든 단어 삭제'):
    st.session_state.words = []

if st.button('모든 삭제된 단어 복원'):
    st.session_state.words = st.session_state.deleted_words if 'deleted_words' in st.session_state else []

if 'deleted_words' in st.session_state:
    with st.expander("삭제된 단어 보기"):
        display_words(st.session_state.deleted_words)

# Usage instructions
st.markdown("## 앱 사용법")
st.markdown("""
1. 관련 사이트와 소셜 미디어 채널에 접속할 수 있는 링크를 클릭하세요.
2. 정리되지 않은 영어 단어 리스트를 텍스트 영역에 입력합니다. 한 줄에 한 단어씩 입력하거나 공백으로 구분하여 여러 단어를 입력할 수 있습니다.
3. 입력한 단어 리스트는 자동으로 분석되어 의미, 동의어, 반의어 등의 정보와 함께 표시됩니다.
4. '모든 단어 삭제' 버튼을 클릭하여 현재 단어 목록을 삭제할 수 있습니다.
5. '모든 삭제된 단어 복원' 버튼을 클릭하여 삭제된 단어를 복원할 수 있습니다.
6. 단어 목록 아래의 'Excel 파일 다운로드' 링크를 클릭하여 현재 단어 목록을 Excel 파일로 다운로드할 수 있습니다.
""")

st.warning("중요: 앱을 종료하기 전에 반드시 'Excel 파일 다운로드' 링크를 클릭하여 현재 단어 목록을 저장하십시오. 앱을 종료하면 데이터가 사라질 수 있습니다.")
