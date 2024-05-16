import streamlit as st
from PIL import Image
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
from newspaper import Article
import io
import requests
import uuid
import json
import nltk

# Download NLTK resources
nltk.download('punkt')

# Function to fetch news based on a topic
def fetch_news_search_topic(topic):
    site = f'https://news.google.com/rss/search?q={topic}'
    op = urlopen(site)
    rd = op.read()
    op.close()
    sp_page = soup(rd, 'xml')
    news_list = sp_page.find_all('item')
    return news_list

# Function to fetch top news
def fetch_top_news():
    site = 'https://news.google.com/news/rss'
    op = urlopen(site)
    rd = op.read()
    op.close()
    sp_page = soup(rd, 'xml')
    news_list = sp_page.find_all('item')
    return news_list

# Function to fetch news based on category
def fetch_category_news(topic):
    site = f'https://news.google.com/news/rss/headlines/section/topic/{topic}'
    op = urlopen(site)
    rd = op.read()
    op.close()
    sp_page = soup(rd, 'xml')
    news_list = sp_page.find_all('item')
    return news_list

# Function to fetch news poster image
def fetch_news_poster(poster_link):
    try:
        u = urlopen(poster_link)
        raw_data = u.read()
        image = Image.open(io.BytesIO(raw_data))
        st.image(image, width=400, use_column_width=False)
    except:
        image = Image.open('./Meta/no_image.jpg')
        st.image(image, width=400, use_column_width=False)

# Function to display news
def display_news(list_of_news, news_quantity):
    c = 0
    for news in list_of_news:
        c += 1
        st.write(f'**({c}) {news.title.text}**')
        news_data = Article(news.link.text)
        try:
            news_data.download()
            news_data.parse()
            news_data.nlp()
        except Exception as e:
            st.error(e)
        fetch_news_poster(news_data.top_image)
        with st.expander(news.title.text):
            st.markdown(
                f'''<h6 style='text-align: justify;'>{news_data.summary}"</h6>''',
                unsafe_allow_html=True)
            st.markdown(f"[Read more at {news.source.text}...]({news.link.text})")
        st.success("Published Date: " + news.pubDate.text)
        if c >= news_quantity:
            break

# Function to translate text
def translate_text(text, target_languages):
    key = "d007437880634b00bd95fbab546596ad"
    endpoint = "https://api.cognitive.microsofttranslator.com"
    location = "eastus"
    path = '/translate'
    constructed_url = endpoint + path
    translated_texts = []

    for target_language in target_languages:
        params = {
            'api-version': '3.0',
            'from': 'en',
            'to': target_language[:2]
        }
        headers = {
            'Ocp-Apim-Subscription-Key': key,
            'Ocp-Apim-Subscription-Region': location,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
        body = [{'text': text}]
        response = requests.post(constructed_url, params=params, headers=headers, json=body)
        if response.status_code == 200:
            try:
                translated_text = response.json()[0]['translations'][0]['text']
                translated_texts.append(translated_text)
            except KeyError:
                translated_texts.append("Translation Error")
        else:
            translated_texts.append("Translation Error")

    return translated_texts

# Streamlit UI
st.set_page_config(page_title='News Adapt📰: Your Personalized News Source Portal..!👀🌏💬', page_icon='./Meta/newspaper.png')

def run():
    st.title("News Adapt📰: Your Personalized News Source Portal..!👀🌏💬 ")
    
    image = Image.open('./Meta/newspaper.png')
    st.image(image, width=600, use_column_width=False)

    category = ['--Select--', 'Trending🔥 News', 'Favourite💖 Topics', 'Search🔍 Topics']
    cat_op = st.selectbox('Select your Category', category)
    if cat_op == category[0]:
        st.warning('Please select a Type!!')
    elif cat_op == category[1]:
        st.subheader("✅ Here are the Trending🔥 news for you")
        no_of_news = st.slider('Number of News:', min_value=5, max_value=25, step=1)
        news_list = fetch_top_news()
        display_news(news_list, no_of_news)
    elif cat_op == category[2]:
        av_topics = ['Choose Topic', 'WORLD', 'NATION', 'BUSINESS', 'TECHNOLOGY', 'ENTERTAINMENT', 'SPORTS', 'SCIENCE',
                     'HEALTH']
        st.subheader("Choose your favorite Topic")
        chosen_topic = st.selectbox("Choose your favorite Topic", av_topics)
        if chosen_topic == av_topics[0]:
            st.warning("Please Choose the Topic")
        else:
            no_of_news = st.slider('Number of News:', min_value=5, max_value=25, step=1)
            news_list = fetch_category_news(chosen_topic)
            if news_list:
                st.subheader(f"✅ Here are some {chosen_topic} News for you")
                display_news(news_list, no_of_news)
            else:
                st.error(f"No News found for {chosen_topic}")
    elif cat_op == category[3]:
        user_topic = st.text_input("Enter your Topic🔍")
        no_of_news = st.slider('Number of News:', min_value=5, max_value=15, step=1)

        if st.button("Search") and user_topic != '':
            user_topic_pr = user_topic.replace(' ', '')
            news_list = fetch_news_search_topic(topic=user_topic_pr)
            if news_list:
                st.subheader(f"✅ Here are some {user_topic.capitalize()} News for you")
                display_news(news_list, no_of_news)
            else:
                st.error(f"No News found for {user_topic}")
        else:
            st.warning("Please write a Topic Name to Search🔍")

    # Translation Section
    st.sidebar.subheader("Translate Text")
    input_text = st.sidebar.text_area("Enter text to translate", "")
    target_languages = st.sidebar.multiselect("Select target languages", ["French (fr)", "Spanish (es)", "German (de)", "Afrikaans (af)", "Albanian (sq)", "Amharic (am)", "Arabic (ar)", 
"Armenian (hy)", "Azerbaijani (az)", "Basque (eu)", "Belarusian (be)", "Bengali (bn)", "Bosnian (bs)", 
"Bulgarian (bg)", "Catalan (ca)", "Cebuano (ceb)", "Chichewa (ny)", "Chinese (Simplified) (zh)", 
"Chinese (Traditional) (zh-TW)", "Corsican (co)", "Croatian (hr)", "Czech (cs)", "Danish (da)", "Dutch (nl)", 
"English (en)", "Esperanto (eo)", "Estonian (et)", "Filipino (tl)", "Finnish (fi)", "Frisian (fy)", 
"Galician (gl)", "Georgian (ka)", "Greek (el)", "Gujarati (gu)", "Haitian Creole (ht)", "Hausa (ha)", 
"Hawaiian (haw)", "Hebrew (iw)", "Hindi (hi)", "Hmong (hmn)", "Hungarian (hu)", "Icelandic (is)", "Igbo (ig)", 
"Indonesian (id)", "Irish (ga)", "Italian (it)", "Japanese (ja)", "Javanese (jw)", "Kannada (kn)", "Kazakh (kk)", 
"Khmer (km)", "Kinyarwanda (rw)", "Korean (ko)", "Kurdish (Kurmanji) (ku)", "Kurdish (Sorani) (ckb)", "Kyrgyz (ky)", 
"Lao (lo)", "Latin (la)", "Latvian (lv)", "Lithuanian (lt)", "Luxembourgish (lb)", "Macedonian (mk)", "Malagasy (mg)", 
"Malay (ms)", "Malayalam (ml)", "Maltese (mt)", "Maori (mi)", "Marathi (mr)", "Mongolian (mn)", "Myanmar (Burmese) (my)", 
"Nepali (ne)", "Norwegian (no)", "Odia (Oriya) (or)", "Pashto (ps)", "Persian (fa)", "Polish (pl)", "Portuguese (pt)", 
"Punjabi (pa)", "Romanian (ro)", "Russian (ru)", "Samoan (sm)", "Scots Gaelic (gd)", "Serbian (sr)", "Sesotho (st)", 
"Shona (sn)", "Sindhi (sd)", "Sinhala (si)", "Slovak (sk)", "Slovenian (sl)", "Somali (so)", "Sundanese (su)", 
"Swahili (sw)", "Swedish (sv)", "Tajik (tg)", "Tamil (ta)", "Tatar (tt)", "Telugu (te)", "Thai (th)", "Turkish (tr)", 
"Turkmen (tk)", "Ukrainian (uk)", "Urdu (ur)", "Uyghur (ug)", "Uzbek (uz)", "Vietnamese (vi)", "Welsh (cy)", "Xhosa (xh)", 
"Yiddish (yi)", "Yoruba (yo)", "Zulu (zu)"
])
    if st.sidebar.button("Translate"):
        if input_text:
            translated_texts = translate_text(input_text, [lang[:2] for lang in target_languages])
            for i, translated_text in enumerate(translated_texts):
                st.sidebar.write(f"Translated Text ({target_languages[i]}): {translated_text}")
        else:
            st.sidebar.warning("Please enter text to translate")

# Call the run function
run()
