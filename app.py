import streamlit as st
import base64
import requests
from bs4 import BeautifulSoup
from gtts import gTTS
import pandas as pd
from textblob import TextBlob
import os

# Set page configuration with a title and icon
st.set_page_config(
    page_title="단어 암기 학습앱",
    page_icon="📚"
)

# Custom CSS
st.markdown(
    """
    <style>
    /* Change the title color */
    h1 {
        color: #4CAF50;
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

# Display the title
st.title("영어 단어 암기 학습앱")
st.markdown("**단어**를 하나씩 추가해서 학습하세요!")

# Sidebar with usage instructions
st.sidebar.title("사용법 안내")
st.sidebar.markdown(
    """
    ### Darlbit Word Subsumption 사용법
    1. **TXT 파일 업로드**: txt 파일을 업로드하여 단어 목록을 추가합니다.
        - 각 줄에 하나의 단어를 입력하세요.
    2. **단어 목록 확인**: 업로드된 단어 목록을 테이블에서 확인할 수 있습니다.
    3. **발음 듣기**: 단어의 발음을 듣기 위해 '발음 듣기' 옵션을 켭니다.
    4. **필터 사용**: 난이도와 주제로 단어 목록을 필터링합니다.
    5. **삭제된 단어 복원**: 삭제된 단어를 복원할 수 있습니다.
    6. **데이터 다운로드**: 단어 목록을 CSV 파일로 다운로드합니다.

    ### 예제 TXT 파일
    아래 버튼을 클릭하여 예제 TXT 파일을 다운로드 받으세요.
    """
)

# Example TXT download
example_txt = "cogitate\nperspicacious\nloquacious"
b64_example_txt = base64.b64encode(example_txt.encode()).decode()
example_href_txt = f'<a href="data:text/plain;base64,{b64_example_txt}" download="example_words.txt">예제 TXT 파일 다운로드</a>'
st.sidebar.markdown(example_href_txt, unsafe_allow_html=True)

# Initialize session state for words if not already done
if 'words' not in st.session_state:
    st.session_state.words = []

if 'play_pronunciation' not in st.session_state:
    st.session_state.play_pronunciation = True


# Function to fetch word details from an online dictionary
def fetch_word_details(word):
    url = f"https://www.dictionary.com/browse/{word}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        try:
            definition = soup.find("div", {"value": "1"}).text.strip()
        except AttributeError:
            definition = "Definition not found"

        try:
            synonyms = ', '.join([syn.text for syn in soup.find_all("a", {"class": "css-1gyuw4i eh475bn0"})[:5]])
        except AttributeError:
            synonyms = "Synonyms not found"

        try:
            antonyms = ', '.join([ant.text for ant in soup.find_all("a", {"class": "css-lv3ht0 eh475bn0"})[:5]])
        except AttributeError:
            antonyms = "Antonyms not found"

        return definition, synonyms, antonyms
    return "Definition not found", "Synonyms not found", "Antonyms not found"


# Function to generate pronunciation audio
def generate_pronunciation(word):
    tts = gTTS(text=word, lang='en')
    audio_path = f"./{word}.mp3"
    tts.save(audio_path)
    return audio_path


# Upload TXT file
uploaded_file = st.file_uploader("TXT 파일 업로드", type=["txt"])

if uploaded_file is not None:
    words = uploaded_file.getvalue().decode("utf-8").splitlines()
    for new_word in words:
        if new_word:
            definition, synonyms, antonyms = fetch_word_details(new_word)
            audio_path = generate_pronunciation(new_word)

            new_word_entry = {
                "word": new_word,
                "part_of_speech": "N/A",
                "example_sentence": "N/A",
                "synonyms": synonyms,
                "antonyms": antonyms,
                "image_url": "https://via.placeholder.com/150",
                "definition": definition,
                "audio_path": audio_path
            }
            st.session_state.words.append(new_word_entry)
    st.success("TXT 파일에서 단어 리스트가 성공적으로 추가되었습니다!")
    st.experimental_rerun()  # Reload the page to reflect changes

# Toggle switch for pronunciation
st.session_state.play_pronunciation = st.checkbox('발음 듣기', value=st.session_state.play_pronunciation)

# Display the words in columns
columns = st.columns(3)

for i, word_entry in enumerate(st.session_state.words):
    col = columns[i % 3]
    with col.expander(label=word_entry["word"], expanded=False):
        # Display the word
        col.subheader(word_entry["word"])

        # Display part of speech
        col.text(f"품사: {word_entry['part_of_speech']}")

        # Display example sentence
        col.text(f"예문: {word_entry['example_sentence']}")

        # Display synonyms and antonyms
        col.text(f"동의어: {word_entry['synonyms']}")
        col.text(f"반의어: {word_entry['antonyms']}")

        # Display definition
        col.text(f"정의: {word_entry['definition']}")

        # Display word image
        if word_entry["image_url"].startswith("data:image"):
            col.image(word_entry["image_url"], caption=word_entry["word"])
        else:
            col.image(word_entry["image_url"], caption=word_entry["word"])

        # Play pronunciation
        if st.session_state.play_pronunciation:
            col.audio(word_entry["audio_path"], format='audio/mp3', start_time=0)

        # Add delete button
        if col.button('삭제', key=f"delete_{i}"):
            del st.session_state.words[i]
            st.experimental_rerun()  # Reload the page to reflect changes

# Data download
if st.session_state.words:
    data = {
        "단어": [word["word"] for word in st.session_state.words],
        "품사": [word["part_of_speech"] for word in st.session_state.words],
        "예문": [word["example_sentence"] for word in st.session_state.words],
        "동의어": [word["synonyms"] for word in st.session_state.words],
        "반의어": [word["antonyms"] for word in st.session_state.words],
        "정의": [word["definition"] for word in st.session_state.words],
        "이미지 URL": [word["image_url"] for word in st.session_state.words]
    }
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="words.csv">CSV 파일 다운로드</a>'
    st.markdown(href, unsafe_allow_html=True)

# Instructions to save data before closing the app
st.sidebar.markdown(
    """
    ### 데이터 저장 안내
    앱을 종료하기 전에 단어 목록을 CSV 파일로 다운로드하여 데이터를 저장하세요. 
    다음 번에 이 파일을 업로드하여 이전 데이터를 불러올 수 있습니다.
    """
)
