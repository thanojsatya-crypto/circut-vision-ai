import streamlit as st
from PIL import Image
import os
import requests
import json

# ==============================================================================
# ========================== APPLICATION CONFIGURATION ==========================
# ==============================================================================

st.set_page_config(page_title="CircuitVision Engine", page_icon="⚡", layout="wide")

# Minimalist Black & White CSS Styling
st.markdown("""
<style>
    .stApp { background-color: #ffffff; color: #000000; }
    div[data-baseweb="textarea"], div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: #f9f9f9 !important;
        border: 1px solid #000000 !important;
        border-radius: 4px !important;
    }
    textarea, input, select { color: #000000 !important; font-weight: 500 !important; }
    .footer-container {
        text-align: center; padding: 15px 0; margin-top: 40px;
        border-top: 1px solid #000000; font-weight: bold; font-size: 0.9em;
        color: #000000 !important;
    }
    h1, h2, h3, h4, p, label, span { color: #000000 !important; }
</style>
""", unsafe_allow_html=True)

MAX_IMAGE_ATTEMPTS = 3

if "image_upload_count" not in st.session_state:
    st.session_state.image_upload_count = 0

# ==============================================================================
# ========================== SIDEBAR AND BACKEND CONFIG ========================
# ==============================================================================

with st.sidebar:
    st.title("⚙️ Configuration")
    
    # Configure Backend API URL (Collapsed under expander)
    with st.expander("🔧 Advanced Settings"):
        backend_url = st.text_input(
            "Backend API URL:",
            value="https://circuit-vision-ai.up.railway.app",
            help="Change this to your deployed FastAPI backend URL (e.g. https://your-backend.railway.app)"
        )
    
    api_provider = st.selectbox("API Provider:", ["OpenRouter", "Google Gemini", "OpenAI"], index=0)
    user_api_key = st.text_input(f"{api_provider} API Key:", value="", type="password")
    
    if api_provider == "Google Gemini":
        model_options = [
            "gemini-2.5-flash",
            "gemini-2.0-flash"
        ]
    elif api_provider == "OpenRouter":
        model_options = [
            "openai/gpt-4o-mini",
            "google/gemini-2.5-flash",
            "google/gemini-2.0-flash",
            "openrouter/free"
        ]
    else:  # OpenAI
        model_options = [
            "gpt-4o-mini"
        ]
        
    selected_model = st.selectbox("Model Core:", model_options)
    st.caption("ℹ️ Provider is automatically detected based on API Key prefix (e.g. sk-or- for OpenRouter, sk- for OpenAI, AIzaSy for Gemini).")
    st.write(f"📸 Image Quota: **{MAX_IMAGE_ATTEMPTS - st.session_state.image_upload_count}/{MAX_IMAGE_ATTEMPTS}**")
    st.markdown("---")
    st.caption("Developed by: DAMISETTI SATYA THANOJ")

# Fallback structures in case the backend cannot be reached initially
DEFAULT_SEGMENTS = {
    "Circuit Theory & Semiconductor Physics": [1, 2, 3, 4, 10, 21, 23, 26, 40],
    "Hardware Design & Synthesis": [5, 6, 7, 14, 15, 18, 19, 20, 24, 32],
    "Embedded, Digital & Microprocessors": [8, 9, 11, 12, 13, 16, 22, 25, 31, 38],
    "Power & Electrical Machines": [36, 37],
    "Lab Execution, Records & Troubleshooting": [17, 27, 28, 29, 30, 33, 34, 35, 39, 41],
    "Standard Web-Based Project Circuits": [31, 34, 27, 11, 12],
    "New Unknown Circuit Synthesis (Novel)": list(range(1, 42))
}

RULE_TRIGGERS = {}
SEGMENTS = DEFAULT_SEGMENTS

# Fetch metadata from backend
metadata_loaded = False
try:
    res = requests.get(f"{backend_url.strip()}/metadata", timeout=5)
    if res.status_code == 200:
        meta_data = res.json()
        RULE_TRIGGERS = meta_data.get("rule_triggers", {})
        SEGMENTS = meta_data.get("segments", DEFAULT_SEGMENTS)
        metadata_loaded = True
except Exception:
    st.sidebar.warning("⚠️ Could not connect to the Backend API. Operating with fallback segments index.")

# ==============================================================================
# ========================== MAIN WORKSPACE UI =================================
# ==============================================================================

if not user_api_key.strip():
    st.title("CircuitVision Execution Engine")
    st.warning(f"⚠️ Enter your {api_provider} API Key in the sidebar to initialize the workspace.")
    st.stop()

st.title("CircuitVision Execution Engine")
st.markdown("---")

col_input, col_info = st.columns([2, 1])

# ------------- LEFT COLUMN: INPUTS & EXECUTION -------------
with col_input:
    selected_segment = st.selectbox(
        "Domain Selection & Generation Mode:",
        ["Auto-Detect (Keyword Only)"] + list(SEGMENTS.keys())
    )
    
    user_goal = st.text_area(
        "Engineering Parameters or Lab Query:",
        height=150,
        placeholder="e.g., Generate a completely new circuit that combines a 555 timer with a MOSFET to drive a high-power LED array."
    )
    
    remaining_attempts = MAX_IMAGE_ATTEMPTS - st.session_state.image_upload_count
    uploaded_file = None
    if remaining_attempts > 0:
        uploaded_file = st.file_uploader(
            f"Context Image/Schematic ({remaining_attempts} left)",
            type=["png", "jpg", "jpeg"]
        )

    if st.button("🚀 Execute Analysis & Synthesis", type="primary", use_container_width=True):
        if not user_goal.strip():
            st.error("Input cannot be empty.")
        else:
            if selected_segment == "New Unknown Circuit Synthesis (Novel)":
                st.info("🔄 Deep Synthesis Mode Active: Cross-referencing all 41 engineering domains. This may take a few seconds...")
            
            # Form-data submission setup
            data_payload = {
                "user_goal": user_goal.strip(),
                "selected_segment": selected_segment,
                "api_provider": api_provider,
                "user_api_key": user_api_key.strip(),
                "selected_model": selected_model
            }
            
            files_payload = {}
            img_to_display = None
            
            if uploaded_file and st.session_state.image_upload_count < MAX_IMAGE_ATTEMPTS:
                # Cache preview representation
                img_to_display = Image.open(uploaded_file)
                # Rewind file buffer to beginning
                uploaded_file.seek(0)
                files_payload = {
                    "image_file": (uploaded_file.name, uploaded_file, uploaded_file.type)
                }

            with st.spinner("Executing Hardware Synthesis & Engine Routing via Backend..."):
                try:
                    res = requests.post(
                        f"{backend_url.strip()}/synthesize",
                        data=data_payload,
                        files=files_payload if files_payload else None,
                        timeout=90
                    )
                    
                    if res.status_code == 200:
                        # Success: Increment image usage state and render response
                        if img_to_display:
                            st.session_state.image_upload_count += 1
                            st.image(img_to_display, caption="Visual Asset Uploaded", width=400)
                        
                        output_text = res.json().get("output", "No response returned from the server.")
                        st.markdown("### 📋 Execution Output")
                        st.markdown(output_text)
                    else:
                        error_detail = "Unknown error"
                        try:
                            error_detail = res.json().get("detail", res.text)
                        except Exception:
                            error_detail = res.text
                        st.error(f"Execution Halt: Backend returned code {res.status_code} - {error_detail}")
                except Exception as e:
                    st.error(f"Execution Halt: Connection failed to backend service. Check URL. Error: {e}")
                
# ------------- RIGHT COLUMN: KNOWLEDGE BASE INDEX -------------
with col_info:
    st.markdown("### 🔍 Database Index")
    st.caption("Active RAG Domains")
    
    with st.container(height=500):
        if not metadata_loaded:
            st.info("Start the FastAPI backend server to view full active rule configurations.")
        
        for segment_name, rule_ids in SEGMENTS.items():
            st.markdown(f"**{segment_name}**")
            for idx in rule_ids:
                # Key names from JSON are strings
                idx_key = str(idx)
                if idx_key in RULE_TRIGGERS:
                    data = RULE_TRIGGERS[idx_key]
                    with st.expander(f"{idx}. {data['name']}"):
                        st.write(f"`{', '.join(data['keywords'])}`")
            st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# ========================== FOOTER ============================================
# ==============================================================================
st.markdown("""
<div class="footer-container">
    CircuitVision • Decoupled Edition
</div>
""", unsafe_allow_html=True)
