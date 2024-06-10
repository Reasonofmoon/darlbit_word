import streamlit as st
import base64
import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
from textblob import TextBlob

# Set page configuration with a title and icon
st.set_page_config(
    page_title="Darlbit Word Subsumption",
    page_icon="📚"
)

# Custom CSS
st.markdown(
    """
    <style>
    body {
        background-image: url('https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FxlrcU%2FbtsyynNTUpV%2F645uH8YylBDseYgqvXXK5k%2Fimg.png');
        background-size: cover;
    }
    h1 {
        color: #4CAF50;
    }
    .link-box {
        padding: 10px;
        border: 2px solid #4CAF50;
        border-radius: 5px;
        margin: 5px;
        background-color: #f9f9f9;
        text-align: center;
    }
    img {
        max-height: 200px;
    }
    .streamlit-expanderContent {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    [data-testid="stExpander"] button {
        display: none;
    }
    .streamlit-expanderHeader {
        pointer-events: none;
    }
    [data-testid="stImage"] button {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state for words and deleted words if not already done
if 'words' not in st.session_state:
    st.session_state.words = []
if 'deleted_words' not in st.session_state:
    st.session_state.deleted_words = []

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
            ipa = soup.find("span", {"class": "pron-spell-content"}).text.strip()
        except AttributeError:
            ipa = None

        synonyms, antonyms, example_sentence = "Not found", "Not found", "Not found"
        # Fetch synonyms, antonyms and example sentences if available
        try:
            synonyms = ', '.join([syn.text for syn in soup.find_all("a", {"class": "css-1gyuw4i eh475bn0"})[:5]])
        except AttributeError:
            pass

        try:
            antonyms = ', '.join([ant.text for ant in soup.find_all("a", {"class": "css-lv3ht0 eh475bn0"})[:5]])
        except AttributeError:
            pass

        try:
            example_sentence = soup.find("div", {"class": "css-pnw38j e15kc6du6"}).text.strip()
        except AttributeError:
            pass

        return definition, ipa, synonyms, antonyms, example_sentence
    return "Definition not found", None, "Not found", "Not found", "Not found"

# Create columns for the main content and usage guide
col1, col2 = st.columns([3, 1])

with col1:
    # Display the title
    st.title("Darlbit Word Subsumption")

    # Upload CSV file
    uploaded_file = st.file_uploader("CSV 파일 업로드", type=["csv"])

    # Upload text file
    uploaded_text_file = st.file_uploader("텍스트 파일 업로드", type=["txt"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("업로드된 데이터")
        st.dataframe(df)

        # Ensure all necessary columns are present
        required_columns = ['word', 'difficulty', 'topic', 'source', 'important']
        for col in required_columns:
            if col not in df.columns:
                df[col] = 'Unknown' if col != 'important' else False

        words = df['word'].tolist()
        for new_word in words:
            if new_word:
                word_details, ipa, synonyms, antonyms, example_sentence = fetch_word_details(new_word)

                new_word_entry = {
                    "word": new_word,
                    "part_of_speech": "Not found",
                    "example_sentence": example_sentence,
                    "synonyms": synonyms,
                    "antonyms": antonyms,
                    "image_url": "https://via.placeholder.com/150",
                    "difficulty": df.loc[df['word'] == new_word, 'difficulty'].values[0],
                    "topic": df.loc[df['word'] == new_word, 'topic'].values[0],
                    "source": df.loc[df['word'] == new_word, 'source'].values[0],
                    "important": df.loc[df['word'] == new_word, 'important'].values[0],
                    "definition": word_details,
                    "ipa": ipa
                }
                st.session_state.words.append(new_word_entry)
        st.success("CSV 파일에서 단어 리스트가 성공적으로 추가되었습니다!")
        st.experimental_rerun()  # Reload the page to reflect changes

    if uploaded_text_file is not None:
        text = uploaded_text_file.read().decode("utf-8")
        st.text_area("업로드된 텍스트", text, height=200)

        if st.button("입력"):
            blob = TextBlob(text)
            words = list(set(blob.words))

            for new_word in words:
                word_details, ipa, synonyms, antonyms, example_sentence = fetch_word_details(new_word)

                new_word_entry = {
                    "word": new_word,
                    "part_of_speech": "Not found",
                    "example_sentence": example_sentence,
                    "synonyms": synonyms,
                    "antonyms": antonyms,
                    "image_url": "https://via.placeholder.com/150",
                    "difficulty": "Unknown",
                    "topic": "General",
                    "source": "Uploaded Text",
                    "important": False,
                    "definition": word_details,
                    "ipa": ipa
                }
                st.session_state.words.append(new_word_entry)
            st.success("텍스트 파일에서 단어 리스트가 성공적으로 추가되었습니다!")
            st.experimental_rerun()  # Reload the page to reflect changes

    # Filter options
    selected_difficulty = st.selectbox('난이도로 필터', ['모두', '쉬움', '중간', '어려움'])
    selected_topic = st.text_input('주제로 필터')
    show_deleted = st.checkbox('삭제된 단어 보기')

    # Display the words in a table format
    def display_words(words):
        data = []
        for i, word_entry in enumerate(words):
            word_info = {
                "단어": word_entry["word"],
                "품사": word_entry['part_of_speech'],
                "예문": word_entry['example_sentence'],
                "동의어": word_entry['synonyms'],
                "반의어": word_entry['antonyms'],
                "난이도": word_entry['difficulty'],
                "주제": word_entry['topic'],
                "예문 출처": word_entry['source'],
                "정의": word_entry['definition'],
                "발음기호": word_entry['ipa'] if word_entry['ipa'] else "없음",
                "중요 단어": "🌟" if word_entry["important"] else ""
            }
            data.append(word_info)

            st.image(word_entry["image_url"], caption=word_entry["word"])

        df = pd.DataFrame(data)
        st.dataframe(df)

        # Download button for the data
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="words.csv">CSV 파일 다운로드</a>'
        if st.button('CSV 파일 다운로드'):
            st.markdown(href, unsafe_allow_html=True)
            st.stop()

    filtered_words = st.session_state.words
    if selected_difficulty != '모두':
        filtered_words = [word for word in filtered_words if word['difficulty'] == selected_difficulty]
    if selected_topic:
        filtered_words = [word for word in filtered_words if selected_topic.lower() in word['topic'].lower()]

    display_words(filtered_words)

    if show_deleted:
        st.markdown("### 삭제된 단어")
        display_words(st.session_state.deleted_words)

    if st.button('모든 삭제된 단어 복원'):
        st.session_state.words.extend(st.session_state.deleted_words)
        st.session_state.deleted_words = []
        st.experimental_rerun()

with col2:
    st.title("사용법")
    st.markdown(
        """
        ### Darlbit Word Subsumption 사용법
        1. **CSV 파일 업로드**: CSV 파일을 업로드하여 단어 목록을 추가합니다.
            - 필요한 열: `word`, `difficulty`, `topic`, `source`, `important`
        2. **텍스트 파일 업로드**: 분석할 텍스트 파일을 업로드합니다.
        3. **입력 버튼 클릭**: 텍스트를 분석하기 위해 '입력' 버튼을 클릭합니다.
        4. **단어 목록 확인**: 업로드된 단어 목록을 테이블에서 확인할 수 있습니다.
        5. **필터 사용**: 난이도와 주제로 단어 목록을 필터링합니다.
        6. **삭제된 단어 복원**: 삭제된 단어를 복원할 수 있습니다.
        7. **데이터 다운로드**: 단어 목록을 CSV 파일로 다운로드합니다.

        ### 예제 CSV 파일
        아래 버튼을 클릭하여 예제 CSV 파일을 다운로드 받으세요.
        """
    )

    # Example CSV download
    example_data = {
        "word": ["cogitate", "perspicacious", "loquacious"],
        "difficulty": ["어려움", "중간", "쉬움"],
        "topic": ["thinking", "perception", "speaking"],
        "source": ["example.com", "example.com", "example.com"],
        "important": [True, False, True]
    }
    example_df = pd.DataFrame(example_data)
    example_csv = example_df.to_csv(index=False)
    b64_example = base64.b64encode(example_csv.encode()).decode()
    example_href = f'<a href="data:file/csv;base64,{b64_example}" download="example_words.csv">예제 CSV 파일 다운로드</a>'
    st.markdown(example_href, unsafe_allow_html=True)

    # Instructions to save data before closing the app
    st.markdown(
        """
        ### 데이터 저장 안내
        앱을 종료하기 전에 단어 목록을 CSV 파일로 다운로드하여 데이터를 저장하세요. 
        다음 번에 이 파일을 업로드하여 이전 데이터를 불러올 수 있습니다.
        """
    )

# Links at the bottom in a 2x2 grid
st.markdown("### 관련 링크")
link_data = [
    ("🌐", "사이트", "https://spiffy-fig-443.notion.site/Reason-of-Moon-c68af35321f24e418bec2b804adadf7a"),
    ("🐦", "Twitter", "https://twitter.com/reasonofmoon"),
    ("📷", "Instagram", "https://www.instagram.com/darlsam37"),
    ("▶️", "YouTube1", "https://www.youtube.com/@reasonofmoon"),
    ("▶️", "YouTube2", "https://www.youtube.com/@meta_prompt"),
    ("🌙", "Moonlang", "https://moonlang.com")
]

cols = st.columns(2)
for i, (emoji, name, url) in enumerate(link_data):
    with cols[i % 2]:
        st.markdown(f'<div class="link-box"><a href="{url}" target="_blank">{emoji} {name}</a></div>', unsafe_allow_html=True)
