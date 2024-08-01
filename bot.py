import streamlit as st
import google.generativeai as genai
import spacy
import json
from streamlit_js_eval import streamlit_js_eval
from dotenv import load_dotenv
import os

def configure():
    load_dotenv()


configure()


nlp = spacy.load("en_core_web_md")
genai.configure(api_key= os.getenv('API_KEY'))
model_name = 'gemini-pro'

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def send_message(prompt):
    try:
        model = genai.GenerativeModel(model_name)
        
        formatted_history = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.chat_history]
        chat = model.start_chat(history=formatted_history)
        message = {"text": prompt} 
        
        response = chat.send_message(prompt, stream=True)
        response_text = []
        for chunk in response:
            if chunk.text:
                response_text.append(chunk.text)
        full_response = " ".join(response_text).replace("\n", "  \n")  
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.session_state.chat_history.append({"role": "model", "content": full_response})
        return full_response
    except Exception as e:
        st.error(f"Error during chat: {e}")
        return ""

with open('keywords.json', 'r') as f:
    keywords = json.load(f)

# Main title
st.markdown("<h1 style='text-align: center; color: green;'>Chat with AgriBot !</h1>", unsafe_allow_html=True)

# Subheader
st.markdown("<h3 style='text-align: center;'>Ask anything about crop and get the answer</h3>", unsafe_allow_html=True)

# User input section with enhanced style
user_input = st.text_input("Ask me anything about crop diseases or cultivation practices:", key="user_input")

# Function to check similarity using spacy
def is_similar(input_text, keywords, threshold=0.75):
    input_doc = nlp(input_text)
    for keyword in keywords:
        keyword_doc = nlp(keyword)
        if input_doc.similarity(keyword_doc) > threshold:
            return True
    return False

# Function to handle user input
def handle_input(input_text):
    lower_input = input_text.lower()

    # Check for any keywords for each crop
    found_keyword = False
    for crop, info in keywords.items():
        if is_similar(lower_input, info['diseases']):
            found_keyword = True
            response = send_message(f"Tell me treatment practices of {input_text}")
            st.write("<hr>", unsafe_allow_html=True)
            st.markdown(f"<p style='background-color: #f0f0f5; padding: 10px; border-radius: 5px;'> {response}</p>", unsafe_allow_html=True)
            break
        elif is_similar(lower_input, info['cultivation']):
            found_keyword = True
            response = send_message(f"What are the {input_text} for {crop}?")
            st.write("<hr>", unsafe_allow_html=True)
            st.markdown(f"<p style='background-color: #f0f0f5; padding: 10px; border-radius: 5px;'> {response}</p>", unsafe_allow_html=True)
            break

    if not found_keyword:
        st.write("<hr>", unsafe_allow_html=True)
        st.markdown("<p style='color: red;'>Sorry, I couldn't find relevant information based on your input. Please ask about known diseases or cultivation practices.</p>", unsafe_allow_html=True)

# Handle user input
if user_input:
    handle_input(user_input)

# Display chat history 
if st.session_state.chat_history:
  st.markdown("**Chat History:**")
  for message in st.session_state.chat_history:
    if message['role'] == 'user':
      st.markdown(f"<p style='text-align: left; font-weight: bold;'><strong>You:</strong> {message['content']}</p>", unsafe_allow_html=True)
    else:
      st.markdown(f"<p style='background-color: #e6ffe6; padding: 10px; border-radius: 5px;'> {message['content']}</p>", unsafe_allow_html=True)


# Button to ask for a new prompt
if st.button("Ask a New Question"):
  streamlit_js_eval(js_expressions="parent.window.location.reload()")


configure()
