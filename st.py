import streamlit as st
import wikipedia
import hashlib
import speech_recognition as sr
from sklearn.feature_extraction.text import CountVectorizer
from streamlit_chat import message

# ------------------ Topic Extraction ------------------
def extract_topic_from_question(question):
    vectorizer = CountVectorizer(stop_words='english')
    try:
        vectorizer.fit([question])
        keywords = vectorizer.get_feature_names_out()
        for word in question.split():
            if word.istitle() and word.lower() not in ['what', 'how', 'is', 'in']:
                return word
        return max(keywords, key=len) if keywords else "smart city"
    except:
        return "smart city"

# ------------------ Wikipedia Summary ------------------
def get_wikipedia_summary(topic):
    try:
        return wikipedia.summary(topic, sentences=8)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"⚠️ '{topic}' is too broad. Try one of: {', '.join(e.options[:3])}"
    except wikipedia.exceptions.PageError:
        return f"❌ No Wikipedia page found for '{topic}'."
    except Exception as e:
        return f"⚠️ Wikipedia error: {str(e)}"

# ------------------ Wikipedia Links ------------------
def get_wikipedia_links(topic):
    try:
        page = wikipedia.page(topic)
        return page.url
    except:
        return None

# ------------------ Voice Input ------------------
def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Listening for your question...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return ""

# ------------------ Streamlit UI Setup ------------------
st.set_page_config(page_title="Smart City Assistant", page_icon="🌆")
st.markdown("<h1 style='color: #3B82F6;'>🌆 Sustainable Smart City Assistant</h1>", unsafe_allow_html=True)
st.markdown("Ask anything about smart city sustainability across the globe or in <span style='color: green;'>Andhra Pradesh</span> cities.", unsafe_allow_html=True)

# ------------------ Chat History ------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------ Clear Chat ------------------
if st.button("🗑️ Clear Chat History"):
    st.session_state.chat_history = []

# ------------------ Input Method ------------------
st.markdown("### 🔍 Choose input method:")
input_mode = st.radio("", ["Text", "Voice"], horizontal=True)

if input_mode == "Text":
    user_input = st.text_input("💬 Ask a question about smart cities:")
else:
    if st.button("🎤 Start Listening"):
        user_input = get_voice_input()
        st.success(f"🗣️ You asked: {user_input}")
    else:
        user_input = ""

# ------------------ Realtime Query Filter ------------------
realtime_keywords = ["air quality", "pollution", "AQI", "temperature", "weather"]

if user_input:
    if any(word in user_input.lower() for word in realtime_keywords):
        bot_answer = (
            "❌ Real-time data like air quality is not available directly from Wikipedia.\n\n"
            "📌 For real-time info, visit:\n"
            "- [🌐 AQI India – Vijayawada](https://www.aqi.in/dashboard/india/andhra-pradesh/vijayawada)\n"
            "- [🌐 IQAir – Vijayawada](https://www.iqair.com/india/andhra-pradesh/vijayawada)\n"
            "- [🌐 CPCB India](https://cpcb.nic.in/)"
        )
    else:
        topic = extract_topic_from_question(user_input)
        wiki_summary = get_wikipedia_summary(topic)
        wiki_link = get_wikipedia_links(topic)

        if wiki_link:
            wiki_summary += f"\n\n🔗 [Learn more on Wikipedia]({wiki_link})"

        bot_answer = wiki_summary

    # Save conversation
    st.session_state.chat_history.append(("user", user_input))
    st.session_state.chat_history.append(("bot", bot_answer))

# ------------------ Chat Display ------------------
for i, (role, msg) in enumerate(st.session_state.chat_history):
    unique_key = f"{role}_{i}_{hashlib.md5(msg.encode()).hexdigest()}"
    message(msg, is_user=(role == "user"), key=unique_key)
