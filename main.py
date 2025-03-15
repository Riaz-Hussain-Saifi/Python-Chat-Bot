import streamlit as st
import uuid
from datetime import datetime
import os
import requests
import json
from config import API_KEY

# Configure page first
st.set_page_config(
    page_title="MindScope AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #343541;
        color: #ECECF1;
    }
    
    /* Header styles */
    .header {
        background-color: #222222;
        color: white;
        padding: 1rem;
        text-align: center;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 1.5rem;
    }
    
    /* Message styles */
    .user-message {
        background-color: #343541;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    
    .assistant-message {
        background-color: #444654;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #202123;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session states
if 'chats' not in st.session_state:
    st.session_state.chats = {}
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None
if 'chat_titles' not in st.session_state:
    st.session_state.chat_titles = {}
if 'api_working' not in st.session_state:
    st.session_state.api_working = None

# Direct API call function using the exact endpoint from the screenshot
def call_gemini_api(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise exception for HTTP errors
        
        response_json = response.json()
        
        # Extract the text from the response
        if "candidates" in response_json and len(response_json["candidates"]) > 0:
            candidate = response_json["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                parts = candidate["content"]["parts"]
                if len(parts) > 0 and "text" in parts[0]:
                    return parts[0]["text"]
        
        return "I couldn't generate a proper response. Please try again."
    
    except requests.exceptions.RequestException as e:
        return f"API Error: {str(e)}"

# Try to test the API
if st.session_state.api_working is None:
    try:
        test_response = call_gemini_api("Hello")
        if "API Error" in test_response:
            st.session_state.api_working = False
            st.session_state.api_error = test_response
        else:
            st.session_state.api_working = True
    except Exception as e:
        st.session_state.api_working = False
        st.session_state.api_error = str(e)

# Custom responses for when API is not working
def get_fallback_response(prompt):
    """Fallback responses when the API is not working"""
    prompt_lower = prompt.lower()
    
    # Identity/creator questions
    if any(keyword in prompt_lower for keyword in ['who made you', 'who created you', 'your developer']):
        return "I am MindScope AI, created by Riaz Hussain. I'm designed to be your intelligent assistant. How can I help you today?"
    
    # Greeting responses
    if any(greeting in prompt_lower for greeting in ['hello', 'hi', 'hey', 'greetings']):
        return "Hello! I'm MindScope AI. How can I assist you today?"
    
    # Help responses
    if any(help_term in prompt_lower for help_term in ['help', 'can you', 'how to']):
        return "I'd be happy to help you with that! Currently, I'm operating in fallback mode due to API connection issues. My capabilities are limited, but I'll do my best to assist you."
    
    # Default response
    return """I apologize, but I'm currently operating in fallback mode due to API connectivity issues. 
    
The Gemini API connection is experiencing problems. This could be due to:

1. Model naming or version mismatch
2. API key permissions or quotas
3. Service availability in your region

Please try again later when the API service is restored. In the meantime, I can still chat with limited capabilities."""

def get_ai_response(prompt):
    """Get response from AI or fallback if API isn't working"""
    # Check if API is working
    if not st.session_state.api_working:
        return get_fallback_response(prompt)
    
    try:
        # Check for identity/creator questions
        creator_keywords = [
            'who made you', 'who created you', 'who developed you', 'who is your creator',
            'who designed you', 'who programmed you', 'who built you', 'who coded you',
            'your developer', 'your creator', 'your programmer', 'your coder',
            'who owns you', 'who invented you', 'who is behind you', 'who engineered you'
        ]
        
        if any(keyword in prompt.lower() for keyword in creator_keywords):
            responses = [
                "I am MindScope AI, an advanced artificial intelligence created by Riaz Hussain. I specialize in engaging conversations, answering questions, and helping with various tasks. How can I assist you today?",
                
                "I'm MindScope AI, developed by Riaz Hussain - a skilled AI Developer and Software Engineer. I'm designed to be your intelligent companion for discussions, problem-solving, and creative tasks.",
                
                "Thanks for asking! I'm MindScope AI, and I was created by Riaz Hussain, an experienced AI developer. I'm here to help you with any questions or tasks you might have.",
                
                "I'm an AI assistant called MindScope, developed by Riaz Hussain. I combine advanced language understanding with helpful capabilities to assist users like you. What can I help you with?"
            ]
            import random
            return random.choice(responses)
        
        # Generate response using direct API call
        response = call_gemini_api(prompt)
        if "API Error" in response:
            st.session_state.api_working = False
            st.session_state.api_error = response
            return get_fallback_response(prompt)
        return response
    except Exception as e:
        st.session_state.api_working = False
        st.session_state.api_error = str(e)
        return f"I encountered an error while processing your request: {str(e)}. Switching to fallback mode."

def main():
    # Header
    st.markdown("""
        <div class="header">
            <h1 style='font-size: 1.8rem; margin-bottom: 0.5rem;'>🤖 MindScope AI</h1>
            <p style='font-size: 1rem; opacity: 0.9;'>Your Intelligent Companion | Created by Riaz Hussain</p>
            <p style='font-size: 0.9rem; opacity: 0.7; margin-top: 0.3rem;'>
                Advanced AI Assistant • Multi-language Support • 24/7 Availability
            </p>
        </div>
    """, unsafe_allow_html=True)

    # API Status Indicator
    if not st.session_state.api_working:
        st.warning(f"⚠️ API Connection Issue: Operating in fallback mode. Error: {st.session_state.api_error}")

    # Sidebar
    with st.sidebar:
        st.title("💬 Chat History")
        
        if st.button("+ New Chat", key="new_chat"):
            new_chat_id = str(uuid.uuid4())
            st.session_state.current_chat_id = new_chat_id
            st.session_state.chats[new_chat_id] = []
            st.session_state.chat_titles[new_chat_id] = "New Chat"
            st.rerun()

        for chat_id, messages in st.session_state.chats.items():
            title = st.session_state.chat_titles.get(chat_id, "New Chat")
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(f"💭 {title}", key=f"chat_{chat_id}"):
                    st.session_state.current_chat_id = chat_id
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{chat_id}"):
                    del st.session_state.chats[chat_id]
                    del st.session_state.chat_titles[chat_id]
                    if st.session_state.current_chat_id == chat_id:
                        st.session_state.current_chat_id = None
                    st.rerun()

        # API Status Reset Button
        if not st.session_state.api_working:
            if st.button("🔄 Retry API Connection"):
                del st.session_state.api_working
                st.rerun()

        # Developer Information Section
        st.markdown("---")
        with st.expander("👨‍💻 About Developer"):
            st.markdown("""
                ### Riaz Hussain
                I'm a senior student in Quarter 2 at GIAIC (Governor-Sindh Initiative of Artificial Intelligence and Computing). 
                Currently, I'm in my 3rd quarter studying Python and AgentAI while pursuing a Full Stack Developer course.

                #### Skills
                - HTML & CSS
                - ReactJS
                - Node.js
                - Next.js 15
                - TailwindCSS
                - TypeScript
                - JavaScript
                - Python
                
                #### Social Media
                - [LinkedIn](https://www.linkedin.com/in/riaz-hussain-saifi)
                - [GitHub](https://github.com/Riaz-Hussain-Saifi)
                - [YouTube](https://www.youtube.com/@Saifi_Developer)
                - [Facebook](https://www.facebook.com/RiazSaifiDeveloper)
                
                I'm passionate about creating innovative solutions and learning new technologies!
            """)

    # Initialize current chat if none exists
    if st.session_state.current_chat_id is None:
        new_chat_id = str(uuid.uuid4())
        st.session_state.current_chat_id = new_chat_id
        st.session_state.chats[new_chat_id] = []
        st.session_state.chat_titles[new_chat_id] = "New Chat"

    # Chat Container
    chat_container = st.container()
    with chat_container:
        messages = st.session_state.chats.get(st.session_state.current_chat_id, [])
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            with st.chat_message(role):
                st.markdown(content)

    # Input
    user_input = st.chat_input("Message MindScope AI...")

    # Handle Input
    if user_input:
        current_chat = st.session_state.chats.get(st.session_state.current_chat_id, [])
        current_chat.append({"role": "user", "content": user_input})
        
        # Set chat title based on first message if it's a new chat
        if len(current_chat) == 1:
            st.session_state.chat_titles[st.session_state.current_chat_id] = user_input[:30] + "..." if len(user_input) > 30 else user_input
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = get_ai_response(user_input)
                    st.markdown(response)
        
        current_chat.append({"role": "assistant", "content": response})
        st.session_state.chats[st.session_state.current_chat_id] = current_chat

if __name__ == "__main__":
    main()