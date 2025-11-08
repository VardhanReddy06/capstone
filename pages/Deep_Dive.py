import streamlit as st
import base64


st.set_page_config(
    page_title="Deep Dive Report",
    page_icon="🔬",
    layout="wide",
    menu_items={}
)

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

st.title("🔬 Deep Dive Report")

def matches(required, present_list):
    return any(required.lower() in p.lower() or p.lower() in required.lower() for p in present_list)

def generate_extra_insights():
    insights = []

    # --- Skill Coverage ---
    soft_req = set(st.session_state.get("soft_skills_required", []))
    soft_pres = set(st.session_state.get("soft_skills_present", []))
    tech_req = set(st.session_state.get("technical_skills_required", []))
    tech_pres = set(st.session_state.get("technical_skills_present", []))

    soft_coverage = (len([s for s in soft_req if any(s.lower() in p.lower() or p.lower() in s.lower() for p in soft_pres)]) / len(soft_req) * 100) if soft_req else 0
    tech_coverage = (len([t for t in tech_req if any(t.lower() in p.lower() or p.lower() in t.lower() for p in tech_pres)]) / len(tech_req) * 100) if tech_req else 0

    insights.append(f"Soft skills coverage: **{soft_coverage:.1f}%** ({len(soft_req)} required, {len(soft_pres)} present)")
    insights.append(f"Technical skills coverage: **{tech_coverage:.1f}%** ({len(tech_req)} required, {len(tech_pres)} present)")

    # --- Skill Balance ---
    if tech_coverage > soft_coverage:
        insights.append("Profile is **technically stronger** compared to soft skills.")
    elif soft_coverage > tech_coverage:
        insights.append("Profile is **soft-skill oriented** compared to technical skills.")
    else:
        insights.append("Profile shows **balanced soft and technical skills**.")

    # --- Critical Gaps ---
    critical_missing = [r for r in tech_req if not any(r.lower() in p.lower() or p.lower() in r.lower() for p in tech_pres)]
    if critical_missing:
        insights.append("⚠️ Critical technical gaps: " + ", ".join(critical_missing))

    # --- Extra Skills ---
    extra_tech = [p for p in tech_pres if not any(r.lower() in p.lower() or p.lower() in r.lower() for r in tech_req)]
    extra_soft = [p for p in soft_pres if not any(r.lower() in p.lower() or p.lower() in r.lower() for r in soft_req)]
    if extra_tech or extra_soft:
        extras = extra_tech + extra_soft
        insights.append("Candidate brings **extra skills** not in JD: " + ", ".join(extras))

    # --- Soft/Tech Ratio ---
    total_soft = len(soft_pres)
    total_tech = len(tech_pres)
    if total_soft + total_tech > 0:
        ratio = (total_soft / (total_soft + total_tech)) * 100
        insights.append(f"Soft-to-Technical skill ratio: **{ratio:.1f}:{100-ratio:.1f}**")

    # --- Trend Alignment ---
    modern_stack = {"react", "node", "mongodb", "aws"}
    modern_present = [p for p in tech_pres if any(m in p.lower() for m in modern_stack)]
    if modern_present:
        insights.append("✅ Candidate is aligned with modern tech stack trends: " + ", ".join(modern_present))

    fundamentals = {"java", "dsa", "data structures", "algorithms"}
    missing_fundamentals = [f for f in fundamentals if not any(f.lower() in p.lower() or p.lower() in f.lower() for p in tech_pres)]
    if missing_fundamentals:
        insights.append("⚠️ Missing core fundamentals: " + ", ".join(missing_fundamentals))

    # --- Suitability Index ---
    overall_score = st.session_state.get("overall_score", 0)
    skill_score = st.session_state.get("skill_score", 0)
    suitability = round((0.7 * overall_score) + (0.3 * skill_score), 2)
    insights.append(f"Final Suitability Index: **{suitability}/100**")

    return "\n".join(f"- {i}" for i in insights)


if st.session_state.get("analysis_done", False):

    # --- Skills Gap Analysis ---
    st.subheader("Skills Gap Analysis")
    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("### 🤝 Soft Skills")
            required_soft = set(st.session_state.get("soft_skills_required", []))
            present_soft = set(st.session_state.get("soft_skills_present", []))
            missing_soft = [r for r in required_soft if not matches(r, present_soft)]
           
            st.markdown("**Required:** " + ", ".join(required_soft) if required_soft else "No data")
            st.markdown("**Present:** " + ", ".join(present_soft) if present_soft else "No data")

            if missing_soft:
                st.error("**Missing:** " + ", ".join(missing_soft))
            else:
                st.success("All required soft skills are covered.")

    with col2:
        with st.container(border=True):
            st.markdown("### 💻 Technical Skills")
            required_tech = set(st.session_state.get("technical_skills_required", []))
            present_tech = set(st.session_state.get("technical_skills_present", []))
            missing_tech = [r for r in required_tech if not matches(r, present_tech)]

            st.markdown("**Required:** " + ", ".join(required_tech) if required_tech else "No data")
            st.markdown("**Present:** " + ", ".join(present_tech) if present_tech else "No data")

            if missing_tech:
                st.error("**Missing:** " + ", ".join(missing_tech))
            else:
                st.success("All required technical skills are covered.")

    st.markdown("---")

    # --- Recommendations ---
    st.subheader("💡 Recommendations")
    with st.container(border=True):
        recs = st.session_state.get("recommendations", [])
        if recs:
            for i, rec in enumerate(recs, 1):
                st.markdown(f"**{i}. {rec}**")
        else:
            st.info("No recommendations available.")

    st.markdown("---")

    # --- Extra Insights ---
    # --- Extra Insights ---
    st.subheader("Extra Insights")
    with st.container(border=True):
        st.markdown(generate_extra_insights())


else:
    st.warning("⚠️ Please run an analysis on the Dashboard first.")
    st.page_link("home.py", label="🏠 Go to Dashboard", icon="🏠")
