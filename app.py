import streamlit as st
import base64
import requests
from bs4 import BeautifulSoup
from gtts import gTTS
import os
import pandas as pd

# Set page configuration with a title and icon
st.set_page_config(
    page_title="Darlbit Word Subsumption",
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

# Display the title
st.title("Darlbit Word Subsumption")

# Links
links = [
    ("사이트", "https://spiffy-fig-443.notion.site/Reason-of-Moon-c68af35321f24e418bec2b804adadf7a"),
    ("Twitter", "https://twitter.com/reasonofmoon"),
    ("Instagram", "https://www.instagram.com/darlsam37"),
    ("YouTube1", "https://www.youtube.com/@reasonofmoon"),
    ("YouTube2", "https://www.youtube.com/@meta_prompt"),
    ("Moonlang", "https://moonlang.com")
]

for name, url in links:
    st.markdown(f'<div class="link-box"><a href="{url}" target="_blank">{name}</a></div>', unsafe_allow_html=True)

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
    tts = gTTS(text=word, lang='en')
    audio_path = f"./{word}.mp3"
    tts.save(audio_path)
    return audio_path


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

        if st.session_state.play_pronunciation:
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
