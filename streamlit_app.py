import openai
import streamlit as st
import os
import pandas as pd
import datetime

# ✅ Load API key from .env file
client=openai.OpenAI(
    api_key="AIzaSyAe-UTpXDJNWCSboM9kAbwJRnAYjImMI5o", 
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# ✅ Streamlit App UI
st.set_page_config(page_title="SferaAI", page_icon="🤖")

st.title("SferaAI")
st.subheader("SferaAI is still learning and can make mistakes. Your conversation may be recorded for quality improvement of SferaAI.")
st.subheader("Please do not include any personal data in your chat with SferaAI. Your conversation is recorded based on the Privacy Policy of Minda Sfera Sdn Bhd.")

st.markdown(
    """
    <style>
        .chat-container { max-width: 700px; margin: auto; }
        .chat-bubble-user { background-color: #DCF8C6; padding: 10px; border-radius: 10px; margin: 5px; }
        .chat-bubble-ai { background-color: #E3E3E3; padding: 10px; border-radius: 10px; margin: 5px; }
    </style>
    """,
    unsafe_allow_html=True
)

# ✅ Chat History (Session State)
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ✅ Display chat messages
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ✅ Load CSV file (ensure it exists)
csv_path = "test_data.csv"
#if os.path.exists(csv_path):
df = pd.read_csv(csv_path)
#else:
#    raise FileNotFoundError(f"⚠ Error: `{csv_path}` not found.")

# ✅ Define AI's marketing objective
objective = "You are a courteous customer service officer and a sales personnel who answers needs of the client based on the data in the file given."

def extract_relevant_data(question):
    """ Extract relevant data from the CSV based on user question """
    data_summary = df.head(1000).to_string()  # Convert first 1000 rows to text
    return f"Based on the data below, answer the question:\n{data_summary}\n\nQuestion: {question}"

def ask_ai_to_generate_question(topic, aim):
    """ AI generates a question based on the given topic """
    # ✅ Call Google Gemini API
    response = client.chat.completions.create(
        model="gemini-1.5-flash",
        messages=[
            {"role": "system", "content": aim},  # ✅ Google Gemini format
            {"role": "user", "content": f"Generate a courteous welcome question for the user about {topic}."}]
    )

    return response.choices[0].message.content  # ✅ Extract response text

def ask_ai(question):
    """ Ask Google Gemini AI a question based on CSV data """
    prompt = extract_relevant_data(question)

    # ✅ Call Google Gemini API
    response = client.chat.completions.create(
        model="gemini-1.5-flash",
        messages=[
            {"role": "system", "content": objective},  # ✅ Google Gemini format
            {"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content  # ✅ Extract response text

def save_chat_history():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"chat_history_{timestamp}.csv"
    
    with open(filename, "w", encoding="utf-8") as file:
        for msg in st.session_state.messages:
            file.write(f"{msg['role'].upper()}: {msg['content']}\n")
    
    return filename

if "messages" not in st.session_state: 
# ✅ Generate a topic to prompt AI to ask
    topic = "I need help from Minda Sfera."
    question = ask_ai_to_generate_question(topic, objective)
    st.session_state["messages"].append({"role": "ai", "content": question})
    with st.chat_message("ai"):
        st.markdown(question)
    response="Initialising."

msg = st.chat_input("Type here.")

if msg:    
    st.session_state["messages"].append({"role": "user", "content": msg})
    with st.chat_message("user"):
        st.markdown(msg)

response = ask_ai(msg)
st.session_state["messages"].append({"role": "ai", "content": response})
with st.chat_message("ai"):
    st.markdown(response)

if any(exit_word in response.lower() for exit_word in ["thank you", "goodbye", "all the best", "great day"]):
    st.session_state["messages"].append({"role": "ai", "content": "Conversation ended."})
    save_chat = True
else:
    save_chat = False

