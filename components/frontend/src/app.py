import os
import logging
import utils
import streamlit as st
import json
from dotenv import load_dotenv
import requests

load_dotenv()

BACKEND_URL = os.environ.get("BACKEND_URL")
if not BACKEND_URL:
    raise ValueError("BACKEND_URL is not set")

url = f"{BACKEND_URL}/chat"

reqHeaders = {
    'Accept': 'text/event-stream',
    'Content-Type': 'application/json'
}

st.set_page_config(page_title="Movie Recommender Chatbot", page_icon="📄", layout="wide")


@utils.enable_chat_history
def main(): 
    clear_history = False
    with st.sidebar:
        st.title("Movie Recommender Chatbot")
        clear_history = st.checkbox("Clear Chat History")

    user_query = st.chat_input(placeholder="Ask me anything!")
    
    text = ""
    if user_query:
        utils.display_msg(user_query, 'user')
        with st.chat_message("assistant"):
            payload = json.dumps(
                {
                    "message": user_query,
                    "clear_history": clear_history
                }
            )
            
            with st.spinner('Streaming...'):
                response = requests.request("POST", url, headers=reqHeaders, data=payload, stream=True)
                if response.status_code != 200:
                    st.error(f"Error: {response.status_code}")
                    return
            
                text_placeholder = st.empty()
                text = ""
                for line in response.iter_lines():
                    line = line.decode('utf-8')
                    if line and starts_with_data_prefix(line):
                        try:
                            data = json.loads(line[len("data: "):])
                            if 'streamed_text' in data:
                                sentence = data['streamed_text']
                                is_final = data['is_final']
                                text += sentence
                                text_placeholder.markdown(text)
                                if is_final:
                                    break
                        except json.JSONDecodeError as e:
                            logging.info(f"Error processing JSON data: {e}")    
            st.session_state.messages.append({"role": "assistant", "content": text})
            

def starts_with_data_prefix(line):
    return line.startswith('data: ')


if __name__ == "__main__":
    main()