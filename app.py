"""
Code Whisperer - Main Application
This file orchestrates everything. It's the conductor, not the musician.
All logic lives in the other files. This file only connects them.
"""

import streamlit as st
from config import config
from parser import CodeParser
from graph_engine import GraphEngine
from gemini_engine import GeminiEngine
from ui_components import render_sidebar, render_code_input, render_results
from utils import validate_code, rate_limiter

# ---------------------------------------------------------------------------
# Page Setup
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="🧠",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Initialize Components (Cached)
# ---------------------------------------------------------------------------
@st.cache_resource
def get_components():
    return {
        "parser": CodeParser(),
        "graph_engine": GraphEngine(),
    }

components = get_components()

# ---------------------------------------------------------------------------
# Render UI
# ---------------------------------------------------------------------------
st.title(f"🧠 {config.APP_NAME}")
st.caption(config.APP_DESCRIPTION)

api_key = render_sidebar()
code = render_code_input()

# ---------------------------------------------------------------------------
# Analyze Button
# ---------------------------------------------------------------------------
if st.button("🔍 Analyze Code", type="primary", use_container_width=True):
    # Step 1: Validate
    is_valid, error = validate_code(code)
    if not is_valid:
        st.error(error)
        st.stop()
    
    # Step 2: Rate Limit
    if not rate_limiter.is_allowed():
        remaining_time = 60
        st.error(f"Rate limit reached. Please wait approximately {remaining_time} seconds.")
        st.stop()
    
    # Step 3: Parse
    with st.spinner("Parsing code structure..."):
        parsed, parse_error = components["parser"].parse(code)
    
    if parse_error:
        st.error(f"Parse Error: {parse_error}")
        st.stop()
    
    # Step 4: Build Graph
    G = components["graph_engine"].build(parsed)
    
    # Step 5: Render Results
    render_results(parsed, G, components["graph_engine"])
    
    # Step 6: AI Explanation (if API key provided)
    if api_key:
        with st.spinner("Generating AI explanation..."):
            try:
                gemini = GeminiEngine(api_key)
                summary = f"Functions: {[f.name for f in parsed.functions]}\nClasses: {[c.name for c in parsed.classes]}\nEntry Points: {parsed.entry_points}\nOrphans: {parsed.orphans}"
                explanation = gemini.explain_code(code, summary)
                st.divider()
                st.subheader("🧠 AI-Powered Explanation")
                st.markdown(explanation)
            except Exception as e:
                st.warning(f"AI explanation unavailable: {str(e)}")
                st.info("The code structure analysis is still complete in the tabs above.")
    else:
        st.info("💡 Enter your Gemini API key in the sidebar to unlock AI-powered explanations.")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(f"{config.APP_NAME} v{config.APP_VERSION} | Built with ❤️ | Free and open source")