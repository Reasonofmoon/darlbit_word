import streamlit as st
import base64
import requests
from bs4 import BeautifulSoup
from gtts import gTTS
import os
import pandas as pd
import re
from PyDictionary import PyDictionary
import io

# Set page configuration with a title and icon
st.set_page_config(
    page_title="Darlbit Word Subsumption",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown(
    """
    <style>
    /* Change the title color */
    h1 {
        color: #4CAF50;
    }
    /* Box style for links */
    .link-box {
        padding: 10px;
        border: 2px solid #4CAF50;
        border-radius: 5px;
        margin: 5px 0;
        background-color: #f9f9f9;
    }
    /* Set maximum height for images */
    img {
        max-height: 200px;
    }
    /* Center align images and text within the expander */
    .streamlit-expanderContent {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    /* Remove the expander toggle button */
    [data-testid="stExpander"] button {
        display: none;
    }
    /* Prevent the expander from collapsing */
    .streamlit-expanderHeader {
        pointer-events: none;
    }
    /* Remove the fullscreen button on images */
    [data-testid="stImage"] button {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Create columns for the main content and usage guide
col1, col2 = st.columns([3, 1])

with col1:
    # Display the title
    st.title("Darlbit Word Subsumption")

    # Links
    links = [
        ("🌐", "사이트", "https://spiffy-fig-443.notion.site/Reason-of-Moon-c68af35321f24e418bec2b804adadf7a"),
        ("🐦", "Twitter", "https://twitter.com/reasonofmoon"),
        ("📷", "Instagram", "https://www.instagram.com/darlsam37"),
        ("▶️", "YouTube1", "https://www.youtube.com/@reasonofmoon"),
        ("▶️", "YouTube2", "https://www.youtube.com/@meta_prompt"),
        ("🌙", "Moonlang", "https://moonlang.com")
    ]

    link_cols = st.columns(len(links))
    for i, (emoji, name, url) in enumerate(links):
        with link_cols[i]:
            st.markdown(f'<div class="link-box"><a href="{url}" target="_blank">{emoji} {name}</a></div>',
                        unsafe_allow_html=True)

    # Initialize session state for words and deleted words if not already done
    if 'words' not in st.session_state:
        st.session_state.words = []
    if 'deleted_words' not in st.session_state:
        st.session_state.deleted_words = []

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

    # Text area for user input
    user_input = st.text_area("정리되지 않은 영어 단어 리스트 입력")

    if user_input:
        # Extract words from the user input
        words = re.findall(r'\b\w+\b', user_input)

        # Add default values for missing columns
        data = []
        for new_word in words:
            if new_word:
                definition, synonyms, antonyms = fetch_word_details(new_word)

                new_word_entry = {
                    "word": new_word,
                    "definition": definition,
                    "synonyms": synonyms,
                    "antonyms": antonyms
                }
                data.append(new_word_entry)

        st.session_state.words.extend(data)
        st.success("입력한 단어 리스트가 성공적으로 추가되었습니다!")
        st.experimental_rerun()  # Reload the page to reflect changes

    # Display the words in a table format
    def display_words(words):
        data = []
        for word_entry in words:
            word_info = {
                "단어": word_entry["word"],
                "의미": word_entry['definition'],
                "동의어": word_entry['synonyms'],
                "반의어": word_entry['antonyms']
            }
            data.append(word_info)

        df = pd.DataFrame(data)
        st.dataframe(df)

        # Download button for the data
        excel_file = io.BytesIO()
        writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        writer.close()
        excel_file.seek(0)
        b64 = base64.b64encode(excel_file.read()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="words.xlsx">Excel 파일 다운로드</a>'
        st.markdown(href, unsafe_allow_html=True)

    display_words(st.session_state.words)

    if st.button('모든 단어 삭제'):
        st.session_state.deleted_words.extend(st.session_state.words)
        st.session_state.words = []
        st.experimental_rerun()

    if st.button('모든 삭제된 단어 복원'):
        st.session_state.words.extend(st.session_state.deleted_words)
        st.session_state.deleted_words = []
        st.experimental_rerun()

    if st.session_state.deleted_words:
        with st.expander("삭제된 단어 보기"):
            display_words(st.session_state.deleted_words)

with col2:
    st.markdown("## 앱 사용법")
    st.markdown("""
    1. 화면 상단의 링크를 클릭하여 관련 사이트와 소셜 미디어 채널에 접속할 수 있습니다.
    2. 정리되지 않은 영어 단어 리스트를 텍스트 영역에 입력합니다. 한 줄에 한 단어씩 입력하거나 공백으로 구분하여 여러 단어를 입력할 수 있습니다.
    3. 입력한 단어 리스트는 자동으로 분석되어 의미, 동의어, 반의어 등의 정보와 함께 표시됩니다.
    4. '모든 단어 삭제' 버튼을 클릭하여 현재 단어 목록을 삭제할 수 있습니다.
    5. '모든 삭제된 단어 복원' 버튼을 클릭하여 삭제된 단어를 복원할 수 있습니다.
    6. 단어 목록 아래의 'Excel 파일 다운로드' 링크를 클릭하여 현재 단어 목록을 Excel 파일로 다운로드할 수 있습니다.
    """)

    st.warning("중요: 앱을 종료하기 전에 반드시 'Excel 파일 다운로드' 링크를 클릭하여 현재 단어 목록을 저장하십시오. 앱을 종료하면 데이터가 사라질 수 있습니다.")
