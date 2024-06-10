import streamlit as st
import base64
import requests
from bs4 import BeautifulSoup

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

# Initialize session state for words if not already done
if 'words' not in st.session_state:
    st.session_state.words = []


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

        # Additional information can be extracted similarly
        # This is a simple example and may need adjustments based on the actual structure of the website
        return definition
    return "Definition not found"


# Form for adding a new word
with st.form(key='add_word_form', clear_on_submit=True):
    new_word = st.text_input('단어')
    new_part_of_speech = st.text_input('품사')
    new_example_sentence = st.text_input('예문')
    new_synonyms = st.text_input('동의어')
    new_antonyms = st.text_input('반의어')
    new_image_file = st.file_uploader('단어 이미지 파일', type=['png', 'jpg', 'jpeg'])
    new_image_url = st.text_input('단어 이미지 URL')

    submit_button = st.form_submit_button(label='추가')

    if submit_button:
        if new_word and new_part_of_speech:
            if new_image_file:
                new_image_bytes = new_image_file.read()
                new_image_base64 = base64.b64encode(new_image_bytes).decode('utf-8')
                new_image_url = f"data:image/png;base64,{new_image_base64}"

            word_details = fetch_word_details(new_word)

            new_word_entry = {
                "word": new_word,
                "part_of_speech": new_part_of_speech,
                "example_sentence": new_example_sentence,
                "synonyms": new_synonyms,
                "antonyms": new_antonyms,
                "image_url": new_image_url or "https://via.placeholder.com/150",
                "definition": word_details
            }
            st.session_state.words.append(new_word_entry)
            st.success(f"{new_word}을(를) 성공적으로 추가했습니다!")
            st.experimental_rerun()  # Reload the page to reflect changes
        else:
            st.error("단어와 품사를 입력해주세요.")

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

        # Add delete button
        if col.button('삭제', key=f"delete_{i}"):
            del st.session_state.words[i]
            st.experimental_rerun()  # Reload the page to reflect changes
