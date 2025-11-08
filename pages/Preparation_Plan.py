import streamlit as st
import base64

st.set_page_config(
    page_title="Preparation Plan",
    page_icon="📅",
    layout="wide",
    menu_items={}
)

import google.generativeai as genai
import os

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

st.title("📅 Preparation Plan")

# Initialize session state for this page
if "prep_plan_text" not in st.session_state:
    st.session_state.prep_plan_text = None
if "prep_days" not in st.session_state:
    st.session_state.prep_days = 10

if "resume_text" not in st.session_state or not st.session_state.resume_text:
    st.warning("⚠️ Please upload resume & job description in the main page and start analysis first.")
else:
    days = st.number_input(
        "⏳ How many days do you have for preparation?", 
        min_value=1, 
        max_value=365, 
        value=st.session_state.prep_days,
        key="prep_days_input"
    )
    
    # Update session state when value changes
    if days != st.session_state.prep_days:
        st.session_state.prep_days = days
        st.session_state.prep_plan_text = None  # Clear old plan when days change
    
    if st.button("Generate Preparation Plan"):
        if os.getenv("GEMINI_API_KEY"):
            with st.spinner("Generating your personalized preparation plan..."):
                genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                model = genai.GenerativeModel("gemini-2.0-flash")
                prompt = f"""
                Resume: {st.session_state.resume_text[:1500]}
                Job Description: {st.session_state.jd_text[:1500]}
                The candidate has {days} days to prepare.
                
                Suggest a structured preparation plan highlighting:
                - Key technical skills to focus on
                - Missing areas to improve
                - Daily/weekly schedule
                """
                response = model.generate_content(prompt)
                
                # Store the generated plan in session state
                st.session_state.prep_plan_text = response.text
                st.session_state.prep_days = days
            st.rerun()
        else:
            st.error("Gemini API key not configured. Cannot generate plan.")
    
    # Display stored preparation plan if it exists
    if st.session_state.prep_plan_text:
        st.success("✅ Preparation Plan Generated")
        st.write(st.session_state.prep_plan_text)