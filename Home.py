import streamlit as st
import base64
from pathlib import Path
import os

# ------------------- Page Configuration ------------------- #
st.set_page_config(
    page_title="Smart Resume Analyzer",
    page_icon="logo.png",
    layout="wide",
    menu_items={}  # removes hamburger menu
)

# ------------------- Logo Display ------------------- #
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



import re
import os

import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
import plotly.graph_objects as go
import json

# ------------------- Setup ------------------- #
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

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


# Add navigation bar with JavaScript
# Create a session variable for navigation
if "page" not in st.session_state:
    st.session_state.page = "Home"

# Navbar
# ------------------- Navigation Bar ------------------- #
import streamlit as st



# Inject CSS styling
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




# ------------------- Resume PDF Processing ------------------- #
def extract_text(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

# ------------------- Gemini Scoring ------------------- #
def final_score_with_gemini(resume_text, jd_text):
    if not GEMINI_API_KEY:
        return {}

    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
    You are an AI resume-job description evaluator. Provide a structured, ATS-style analysis.

    Resume: {resume_text[:2500]}
    Job Description: {jd_text[:2500]}

    Return output strictly in JSON with the following keys:
    {{
    "overall_score": number (0-100),
    "semantic_score": number (0-100),
    "skill_score": number (0-100),

    "feedback": "Comprehensive qualitative feedback. 
                Break it into sections:
                - Strengths (detailed and contextual, highlight relevant projects/roles).
                - Weaknesses/Missing Skills (list clearly, explain why they matter).
                - Opportunities (where the resume could be tailored more).
                - Risks (any red flags like gaps, vague descriptions).
                Provide at least 2-3 points under each section.",

    "soft_skills_required": ["list of soft skills from JD"],
    "soft_skills_present": ["soft skills inferred from resume"],
    "technical_skills_required": ["list of technical skills required from JD"],
    "technical_skills_present": ["technical skills present in resume"],

    "recommendations": [
        "Provide at least 5 tailored suggestions to improve the resume. 
        Suggestions should include keyword enrichment, ATS optimization, 
        quantifying impact (numbers/metrics), highlighting projects, 
        and aligning achievements with JD."
    ]
    }};
    """


    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # Try direct JSON parse
        try:
            result = json.loads(raw_text)
        except:
            # Extract JSON substring if extra text exists
            match = re.search(r"\{.*\}", raw_text, re.S)
            if match:
                result = json.loads(match.group(0))
            else:
                raise ValueError("No valid JSON found in Gemini response")

        return result

    except Exception as e:
        return {"error": str(e)}

# ------------------- Plotly Gauge ------------------- #
def circular_gauge(label, value, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': label, 'font': {'size': 20, 'color': '#333'}},
        number={'suffix': "%", 'font': {'size': 28, 'color': color}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#ccc",
        }
    ))
    fig.update_layout(height=250, margin=dict(t=40, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

def get_color(value):
    if value <= 40:
        return "red"
    elif 41 <= value <= 70:
        return "orange"
    else:
        return "green"

# ------------------- Streamlit UI ------------------- #
st.title("📄 Job Description Based Resume Analyzer")

# ------------------- Session State ------------------- #
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "jd_text" not in st.session_state:
    st.session_state.jd_text = None
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "resume_file_key" not in st.session_state:
    st.session_state.resume_file_key = 0
if "jd_input_key" not in st.session_state:
    st.session_state.jd_input_key = 0

# Store results (main metrics)
if "overall_score" not in st.session_state:
    st.session_state.overall_score = None
if "semantic_score" not in st.session_state:
    st.session_state.semantic_score = None
if "skill_score" not in st.session_state:
    st.session_state.skill_score = None
if "feedback_text" not in st.session_state:
    st.session_state.feedback_text = None

# Store extra analysis (for Deep Dive)
if "soft_skills_required" not in st.session_state:
    st.session_state.soft_skills_required = []
if "soft_skills_present" not in st.session_state:
    st.session_state.soft_skills_present = []
if "technical_skills_required" not in st.session_state:
    st.session_state.technical_skills_required = []
if "technical_skills_present" not in st.session_state:
    st.session_state.technical_skills_present = []
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []

# ------------------- Buttons ------------------- #
colA, colB = st.columns([1, 1])

with colB:
    if st.button("New Analysis", use_container_width=True, help="Start a fresh analysis"):
        for key in list(st.session_state.keys()):
            if key not in ["resume_file_key", "jd_input_key"]:
                st.session_state[key] = None
        st.session_state.analysis_done = False
        st.session_state.resume_file_key += 1
        st.session_state.jd_input_key += 1
        st.rerun()

# ------------------- File & JD Input ------------------- #
st.markdown("### 📎 Upload Your Resume")
resume_file = st.file_uploader(
    "",  # Remove label as we use markdown above
    type="pdf",
    key=f"resume_{st.session_state.resume_file_key}",
    disabled=st.session_state.analysis_done
)

jd_input = st.text_area(
    "Enter Job Description Here",
    height=200,
    key=f"jd_{st.session_state.jd_input_key}",
    disabled=st.session_state.analysis_done,
    value=st.session_state.jd_text if st.session_state.analysis_done else ""
)

# ------------------- Submit Analysis Button ------------------- #
with colA:
    start_btn = st.button(" Start Analysis", use_container_width=True, disabled=st.session_state.analysis_done, help="Click to analyze your resume")

# ------------------- Submit Analysis ------------------- #
if start_btn:
    if resume_file and jd_input.strip():
        with st.spinner("Analyzing resume with Gemini AI..."):
            st.session_state.resume_text = extract_text(resume_file.read())
            st.session_state.jd_text = jd_input.strip()

            result = final_score_with_gemini(
                st.session_state.resume_text,
                st.session_state.jd_text
            )

            # Store only the needed ones for Home page
            st.session_state.overall_score = result.get("overall_score", 0)
            st.session_state.semantic_score = result.get("semantic_score", 0)
            st.session_state.skill_score = result.get("skill_score", 0)
            st.session_state.feedback_text = result.get("feedback", "No feedback provided")

            # Store extras for Deep Dive
            st.session_state.soft_skills_required = result.get("soft_skills_required", [])
            st.session_state.soft_skills_present = result.get("soft_skills_present", [])
            st.session_state.technical_skills_required = result.get("technical_skills_required", [])
            st.session_state.technical_skills_present = result.get("technical_skills_present", [])
            st.session_state.recommendations = result.get("recommendations", [])

            st.session_state.analysis_done = True

        st.rerun()
    else:
        st.warning("⚠ Please upload a resume and enter a job description before submitting.")

# ------------------- Show Analysis ------------------- #
if st.session_state.analysis_done and st.session_state.overall_score is not None:
    st.subheader("📊 Match Scores")
    col1, col2, col3 = st.columns(3)

    with col1:
        circular_gauge("Overall Match", round(st.session_state.overall_score, 2), get_color(st.session_state.overall_score))
    with col2:
        circular_gauge("Semantic Similarity", round(st.session_state.semantic_score, 2), get_color(st.session_state.semantic_score))
    with col3:
        circular_gauge("Skill Match", round(st.session_state.skill_score, 2), get_color(st.session_state.skill_score))

    st.subheader("📝 Qualitative Feedback")
    st.write(st.session_state.feedback_text)
