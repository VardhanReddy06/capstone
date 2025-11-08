import streamlit as st

st.set_page_config(
    page_title="Resume Chatbot",
    layout="wide",
    menu_items={}
)

import os
import base64
 # PyMuPDF
import google.generativeai as genai
from dotenv import load_dotenv

# ------------------- Configuration ------------------- # 
load_dotenv()

# Read API key directly from .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("❌ No Google API key found. Please set GOOGLE_API_KEY in your .env file.")
else:
    genai.configure(api_key=GEMINI_API_KEY)\
    
def get_base64_of_image(image_path):
    """Convert image to base64 to ensure it displays correctly in Streamlit."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

try:
    logo_base64 = get_base64_of_image("logo.png")  # Make sure 'logo.png' is in the same folder
    st.markdown(
    f"""
    <div style='display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 20px;'>
        <img src='data:image/png;base64,{logo_base64}'
             style='width:110px; height:110px; border-radius:50%; object-fit:contain;'>
        <h1 style='color: #D9D9D9; font-family: "Segoe UI", sans-serif; font-size: 42px; margin: 0;'>
            Smart Resume Analyzer
        </h1>
    </div>
    """,
    unsafe_allow_html=True
)

except FileNotFoundError:
    st.error("⚠ logo.png not found. Please ensure the logo file is in the same directory.")

st.markdown("""
    <style>
        /* Remove sidebar and its toggle completely */
        [data-testid="stSidebar"], [data-testid="collapsedControl"] {
            display: none !important;
        }
        /* Make app full-width */
        .block-container {
            padding-left: 3rem !important;
            padding-right: 3rem !important;
            max-width: 100% !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

div[data-testid="stHorizontalBlock"] {
    display: flex;
    justify-content: center;
    padding: 12px 0;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
    margin-bottom: 25px;
}

a[data-testid="stPageLink-NavLink"] {
    color: #E0E0E0 !important;  /* Whitish grey text */
    font-weight: 600;
    font-size: 18px;
    text-decoration: none;
    padding: 10px 25px;
    border-radius: 10px;
    transition: all 0.3s ease;
}

a[data-testid="stPageLink-NavLink"]:hover {
    background-color: #333333;
    color: #FFFFFF !important;
    transform: scale(1.05);
}

a[data-testid="stPageLink-NavLink"] > span {
    margin-right: 6px;
}
</style>
""", unsafe_allow_html=True)

# Navbar layout
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.page_link("Home.py", label="Home", icon="🛖")
with col2:
    st.page_link("pages/Chat_with_Resume.py", label="Chat", icon="💬")
with col3:
    st.page_link("pages/Deep_Dive.py", label="Deep Dive", icon="🔬")
with col4:
    st.page_link("pages/Preparation_Plan.py", label="Plan", icon="📅")

# ------------------- PDF Processing ------------------- # 
@st.cache_data(show_spinner="📖 Extracting resume text...")
def extract_text_cached(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

# ------------------- Ask Gemini ------------------- # 
def ask_gemini(history, resume_text, new_question):
    chat_history = "\n".join(history)
    prompt = f"""
You are an AI assistant that gives **detailed, step-by-step, professional answers** 
based only on the given resume.

Resume:
\"\"\" 
{resume_text}
\"\"\"

Conversation so far:
{chat_history}

Rules:
1. Always analyze the question before answering.
2. Provide at least 3–5 sentences per answer (structured and professional).
3. Only answer based on the resume.
4. If unrelated to resume, reply: "I can only answer based on the resume."
5. Use formatting (bullet points, numbered steps) if it improves clarity.

Q: {new_question}
A:"""

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

# ------------------- Streamlit App ------------------- #

# ------------------- Initialize session state ------------------- #
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None

st.title("💬 Chat with Your Resume")

# ------------------- Reset Button ------------------- #
if st.button("🆕 New Chat"):
    st.session_state.chat_history = []
    st.session_state.resume_text = None
    st.session_state.last_uploaded_file = None
    st.rerun()   # refresh app state immediately

# ------------------- File Upload ------------------- #
uploaded_file = st.file_uploader("📁 Upload your Resume (PDF)", type="pdf")

if uploaded_file:
    # Check if a new file is uploaded
    if st.session_state.last_uploaded_file != uploaded_file.name:
        # Reset everything for new file
        st.session_state.resume_text = None
        st.session_state.chat_history = []
        st.session_state.last_uploaded_file = uploaded_file.name

    if st.session_state.resume_text is None:
        file_bytes = uploaded_file.read()
        text = extract_text_cached(file_bytes)
        if not text:
            st.warning("❌ The resume has no readable text.")
            st.stop()
        st.session_state.resume_text = text
        st.success("✅ Resume uploaded and processed!")

# ------------------- Chat Interface ------------------- #
if st.session_state.resume_text:
    # Display previous messages
    for entry in st.session_state.chat_history:
        if entry.startswith("Q:"):
            st.chat_message("user").write(entry[2:].strip())
        elif entry.startswith("A:"):
            st.chat_message("assistant").write(entry[2:].strip())

    # Chat input
    user_input = st.chat_input("Ask something about the resume...")

    if user_input:
        st.chat_message("user").write(user_input)
        st.session_state.chat_history.append(f"Q: {user_input}")

        with st.chat_message("assistant"):
            response = ask_gemini(
                st.session_state.chat_history,
                st.session_state.resume_text,
                user_input,
            )
            st.write(response)
            st.session_state.chat_history.append(f"A: {response}")
else:
    st.info("⬆️ Please upload your resume above to start chatting.")