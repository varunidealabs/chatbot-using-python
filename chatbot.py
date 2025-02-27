import streamlit as st
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Store API configuration in environment variables or constants

API_KEY = st.secrets["general"]["AZURE_API_KEY"]
API_ENDPOINT = st.secrets["general"]["AZURE_API_ENDPOINT"]
API_VERSION = st.secrets["general"]["AZURE_API_VERSION"]
DEPLOYMENT_NAME = st.secrets["general"]["AZURE_DEPLOYMENT_NAME"]

# App title and configuration
st.set_page_config(
    page_title="AI Assistant Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stApp {
        background-color: #f5f7f9;
    }
    .chat-message {
        padding: 1.5rem; 
        border-radius: 0.8rem; 
        margin-bottom: 1rem; 
        display: flex;
        flex-direction: row;
        align-items: flex-start;
        gap: 0.75rem;
    }
    .chat-message.user {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
        color: #000000;
    }
    .chat-message.assistant {
        background-color: #f1f8e9;
        border-left: 5px solid #8bc34a;
        color: #000000;
    }
    .chat-message .avatar {
        width: 35px;
        height: 35px;
        border-radius: 50%;
        object-fit: cover;
        flex-shrink: 0;
    }
    .chat-message .message-content {
        flex-grow: 1;
        color: #000000;
    }
    .chat-message .timestamp {
        color: #333333;
        font-size: 0.8rem;
        margin-top: 0.3rem;
    }
    /* Input box styling */
    .stTextInput>div>div>input {
        border-radius: 0.5rem;
        border: 2px solid #3498DB !important;
        background-color: #EBF5FB !important;
        color: #000000 !important;
        font-weight: 500;
        caret-color: #000000;
    }
    .stTextInput>div>div>input:focus {
        border: 2px solid #2E86C1 !important;
        box-shadow: 0 0 5px rgba(46, 134, 193, 0.5);
    }
    /* Send button styling */
    .stButton>button {
        background-color: #2E86C1 !important;
        color: white !important;
        border: none !important;
        border-radius: 0.5rem !important;
        padding: 0.5rem 1rem !important;
        font-weight: bold !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1A5276 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .stButton>button:active {
        transform: translateY(0px);
    }
    
    .typing-indicator {
        display: flex;
        align-items: center;
        margin-top: 0.5rem;
    }
    .typing-dot {
        width: 8px;
        height: 8px;
        margin: 0 1px;
        background-color: #8bc34a;
        border-radius: 50%;
        animation: typing-dot-animation 1.5s infinite ease-in-out;
    }
    .typing-dot:nth-child(1) { 
        animation-delay: 0s; 
    }
    .typing-dot:nth-child(2) { 
        animation-delay: 0.5s; 
    }
    .typing-dot:nth-child(3) { 
        animation-delay: 1s; 
    }
    @keyframes typing-dot-animation {
        0% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.5); opacity: 1; }
        100% { transform: scale(1); opacity: 0.5; }
    }
    /* Title styles */
    h1, h2, h3, p {
        color: #000000 !important;
    }
    .main-title {
        color: #2E7D32 !important;
        font-weight: bold;
    }
    .subtitle {
        color: #1565C0 !important;
        font-weight: 500;
    }
    /* Sidebar styles */
    .css-1d391kg, .css-12oz5g7 {
        background-color: #2C3E50;
    }
    .sidebar .sidebar-content {
        background-color: #2C3E50;
    }
    [data-testid="stSidebar"] {
        background-color: #2C3E50;
    }
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background-color: #3498DB;
        color: white;
        border: none;
        border-radius: 4px;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #2980B9;
    }
    [data-testid="stSidebar"] .stSlider > div {
        color: white;
    }
    [data-testid="stSidebar"] .stCheckbox label {
        color: white !important;
    }
    [data-testid="stSidebar"] .stCheckbox label span p {
        color: white !important;
    }
    /* Fix for slider text */
    [data-testid="stSidebar"] .stSlider label span {
        color: white !important;
    }
    /* For success messages */
    [data-testid="stSidebar"] .element-container div[data-testid="stText"] {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_started" not in st.session_state:
    st.session_state.conversation_started = False
if "loading" not in st.session_state:
    st.session_state.loading = False
if "user_input" not in st.session_state:
    st.session_state.user_input = ""




# Function to handle message submission
def submit_message():
    if st.session_state.user_input:
        # Add user message to conversation
        current_time = datetime.now().strftime("%H:%M:%S")
        st.session_state.messages.append({
            "role": "user",
            "content": st.session_state.user_input,
            "timestamp": current_time
        })
        
        # Clear input field and set states for processing
        user_message = st.session_state.user_input
        st.session_state.user_input = ""
        st.session_state.conversation_started = True
        st.session_state.loading = True

# Sidebar configuration
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Model parameters
    st.subheader("Model Parameters")
    temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=0.7, step=0.1,
                          help="Higher values make output more random, lower values more deterministic")
    max_tokens = st.slider("Max Response Length", min_value=50, max_value=4000, value=1000, step=50,
                         help="Maximum number of tokens to generate in the response")
    
    # UI Options
    st.subheader("UI Options")
   
    enable_typing_animation = st.checkbox("Enable Typing Animation", value=True)
    
    # Clear conversation button
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.conversation_started = False
        st.session_state.loading = False
        st.session_state.user_input = ""
        st.success("Conversation cleared!")
    
    # About section    
    st.subheader("About")
    st.markdown("""
    This chatbot application connects to Azure's GPT-4o API to provide 
    intelligent responses to your questions and conversations.
    
    **How to use:**
    1. Enter your message in the text box below
    2. Press Enter or click the "Send" button
    3. Wait for the AI to respond
    
    Made with ❤️ by VARUN
    """)

# Main chat interface
st.markdown('<h1 class="main-title">🤖 AI Assistant Chat</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Have a conversation with GPT-4o - ask questions, get help, or just chat!</p>', unsafe_allow_html=True)

# Helper function to call Azure OpenAI API
def call_azure_openai_api(messages, temperature=0.7, max_tokens=1000):
    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY,
    }
    
    endpoint_url = f"{API_ENDPOINT}/openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version={API_VERSION}"
    
    payload = {
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    
    try:
        response = requests.post(endpoint_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for 4XX/5XX status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

# Function to display chat messages
def display_messages():
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        timestamp = message.get("timestamp", "")
        
        if role == "user":
            avatar = "👤"
            message_class = "user"
        elif role == "assistant":
            avatar = "🤖"
            message_class = "assistant"
        else:
            continue  # Skip system messages
        
        col1, col2 = st.columns([12, 1])
        with col1:
            # display of message
            st.markdown(f"""
            <div class="chat-message {message_class}">
                <div class="avatar">{avatar}</div>
                <div class="message-content">
                    <div>{content}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Function to display typing indicator
def display_typing_indicator():
    if enable_typing_animation and st.session_state.loading:
        st.markdown("""
        <div class="chat-message assistant">
            <div class="avatar">🤖</div>
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Display welcome message if conversation not started
if not st.session_state.conversation_started:
    st.markdown("""
    <div class="chat-message assistant">
        <div class="avatar">🤖</div>
        <div class="message-content">
            <div>Hello! I'm your AI assistant powered by GPT-4o. How can I help you today?</div>
            <div class="timestamp">Just now</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Display previous messages
display_messages()

# Display typing indicator when loading
display_typing_indicator()

# Message input
with st.container():
    # Use columns for input and button
    col1, col2 = st.columns([6, 1])
    
    with col1:
        # Use callback function to handle Enter key press
        st.text_input(
            "Type your message here...", 
            key="user_input", 
            on_change=submit_message,
            label_visibility="collapsed"
        )
    
    with col2:
        if st.button("Send 📤"):
            submit_message()

# Process the API call and display response after rerun
if st.session_state.loading and len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    try:
        # Convert messages for API call
        api_messages = [
            {"role": "system", "content": "You are a helpful and friendly AI assistant powered by GPT-4o. Provide accurate, concise, and helpful responses."}
        ]
        for msg in st.session_state.messages:
            api_messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Call the API
        response_data = call_azure_openai_api(
            api_messages, 
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Process response
        if response_data and "choices" in response_data and len(response_data["choices"]) > 0:
            assistant_response = response_data["choices"][0]["message"]["content"]
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # Add assistant response to conversation
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_response,
                "timestamp": current_time
            })
        else:
            # Handle API error
            st.error("Failed to get a response from the AI. Please check your API settings.")
    except Exception as e:
        st.error(f"Error: {str(e)}")
    finally:
        # Reset loading state
        st.session_state.loading = False
        
        # Trigger a rerun to update the UI with the new message
        st.rerun()

# Add a footer
st.markdown("""
<div style="text-align: center; margin-top: 2rem; padding: 1rem; color: #333333;">
    <hr>
    <p>© 2025 AI Assistant Chat | Powered by Azure OpenAI GPT-4o</p>
</div>
""", unsafe_allow_html=True)
