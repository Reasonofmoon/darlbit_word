import streamlit as st
import base64
import requests
from bs4 import BeautifulSoup
from gtts import gTTS
from gtts.tts import gTTSError
import os
import pandas as pd

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


    # Function to generate pronunciation audio
    def generate_pronunciation(word):
        try:
            tts = gTTS(text=word, lang='en')
            audio_path = f"./{word}.mp3"
            tts.save(audio_path)
            return audio_path
        except gTTSError as e:
            return None


    # Upload CSV file
    uploaded_file = st.file_uploader("CSV 파일 업로드", type=["csv"])

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
                audio_path = generate_pronunciation(new_word)

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
                    "ipa": ipa,
                    "audio_path": audio_path
                }
                if new_word not in [word_entry["word"] for word_entry in st.session_state.words]:
                    st.session_state.words.append(new_word_entry)
        st.success("CSV 파일에서 단어 리스트가 성공적으로 추가되었습니다!")
        st.experimental_rerun()  # Reload the page to reflect changes

    # Toggle switch for pronunciation
    st.session_state.play_pronunciation = st.checkbox('발음 듣기', value=st.session_state.play_pronunciation)

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

            if st.session_state.play_pronunciation and word_entry["audio_path"]:
                st.audio(word_entry["audio_path"], format='audio/mp3', start_time=0)
            st.image(word_entry["image_url"], caption=word_entry["word"])

        df = pd.DataFrame(data)
        st.dataframe(df)

        # Download button for the data
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="words.csv">CSV 파일 다운로드</a>'
        st.markdown(href, unsafe_allow_html=True)


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
    st.markdown("## 앱 사용법")
    st.markdown("""
    1. 화면 상단의 링크를 클릭하여 관련 사이트와 소셜 미디어 채널에 접속할 수 있습니다.
    2. CSV 파일을 업로드하여 단어 리스트를 추가할 수 있습니다. 파일에는 'word', 'difficulty', 'topic', 'source', 'important' 열이 포함되어야 합니다.
    3. '발음 듣기' 체크박스를 선택하여 단어의 발음을 들을 수 있습니다.
    4. '난이도로 필터'와 '주제로 필터' 옵션을 사용하여 단어를 필터링할 수 있습니다.
    5. '삭제된 단어 보기' 체크박스를 선택하여 삭제된 단어를 확인할 수 있습니다.
    6. '모든 삭제된 단어 복원' 버튼을 클릭하여 삭제된 단어를 복원할 수 있습니다.
    7. 단어 목록 아래의 'CSV 파일 다운로드' 링크를 클릭하여 현재 단어 목록을 CSV 파일로 다운로드할 수 있습니다.
    """)

    st.warning("중요: 앱을 종료하기 전에 반드시 'CSV 파일 다운로드' 링크를 클릭하여 현재 단어 목록을 저장하십시오. 앱을 종료하면 데이터가 사라질 수 있습니다.")

    st.markdown("## 사용자 정의 단어장 만들기")
    st.markdown("""
    1. 엑셀이나 구글 시트 등을 사용하여 새로운 단어장을 만듭니다.
    2. 다음 열을 포함하도록 단어장을 구성합니다:
       - word: 단어
       - difficulty: 난이도 (쉬움, 중간, 어려움)
       - topic: 주제
       - source: 단어의 출처 또는 예문
       - important: 중요한 단어 여부 (True 또는 False)
    3. 단어장을 CSV 파일로 저장합니다.
    4. 앱에서 'CSV 파일 업로드'를 클릭하고 저장한 CSV 파일을 선택하여 업로드합니다.
    """)

# Create an example CSV file
example_data = {
    'word': ['diligent', 'procrastinate', 'resilient', 'feasible', 'verbose'],
    'difficulty': ['중간', '어려움', '중간', '쉬움', '어려움'],
    'topic': ['personality', 'time management', 'personality', 'general', 'communication'],
    'source': [
        'She is a diligent student who always completes her assignments on time.',
        'I tend to procrastinate when it comes to doing my taxes.',
        'Despite facing numerous setbacks, he remained resilient and never gave up on his dreams.',
        'The proposed plan seems feasible and can be implemented within the given timeframe.',
        'The verbose speaker tended to ramble on without getting to the point.'
    ],
    'important': [True, False, True, False, False]
}
example_df = pd.DataFrame(example_data)
example_csv = example_df.to_csv(index=False)
b64 = base64.b64encode(example_csv.encode()).decode()
href = f'<a href="data:file/csv;base64,{b64}" download="example.csv">예제 CSV 파일 다운로드</a>'
st.markdown(href, unsafe_allow_html=True)