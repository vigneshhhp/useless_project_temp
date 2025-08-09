import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re
import io
import os
from dotenv import dotenv_values
config = dotenv_values(".env")

# Load variables from .env
# load_dotenv()
# print(load_dotenv())

# Get the key
# API_KEY = os.getenv("GEMINI_API_KEY")
API_KEY = config["GEMINI_API_KEY"]

import google.generativeai as genai
genai.configure(api_key=API_KEY)

# ==============================
# CONFIGURATION
# ==============================
#genai.configure(api_key="API_KEY")  # Replace with your actual Gemini API key

# Models
analyzer_model = genai.GenerativeModel('gemini-1.5-flash')
roast_model = genai.GenerativeModel('gemini-1.5-pro')

# Prompts
ANALYSIS_PROMPT = """
You are an expert in Keralite cuisine. Analyze the provided image of a Sadhya served on a banana leaf. 
Identify each dish and estimate the percentage remaining. 
Return ONLY a JSON list where each item has 'dish_name' and 'percentage_remaining'.
"""

ROAST_PROMPT_TEMPLATE = """
You are a sharp-tongued and dramatic Malayali Ammachi.
Be sarcastic, funny, and dramatic, but still good-natured.
Roast based on this leftover data:
{leftovers}
"""

# ==============================
# STREAMLIT PAGE CONFIG
# ==============================
st.set_page_config(layout="wide", page_title="AI Sadhya Critic 🍌🍛")
st.markdown(
    """
    <style>
    body {
        background-color: #f3f9f1;
    }
    .stButton>button {
        background-color: #6ab04c;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        height: 3em;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #58a03c;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================
# APP TITLE
# ==============================
st.title("🌿 AI Sadhya Leaf Analyzer & Ammachi’s Judgement 🧐")
st.write("Upload your **banana leaf after eating** and let our AI Ammachi roast you like a true Kerala grandma!")

uploaded_file = st.file_uploader("📷 Upload your Sadhya plate photo...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    img_bytes = io.BytesIO()
    image.save(img_bytes, format=image.format)
    img_bytes.seek(0)

    st.image(image, caption="Your Sadhya Plate", use_container_width=True)
    st.divider()

    if st.button("🍴 Analyze & Get Roasted!", type="primary"):
        with st.spinner("Ammachi is inspecting your plate..."):
            try:
                # --- Analysis ---
                response = analyzer_model.generate_content(
                    [ANALYSIS_PROMPT, {"mime_type": uploaded_file.type, "data": img_bytes.getvalue()}]
                )

                text_output = response.text.strip()

                # Try extracting JSON
                match = re.search(r"\[.*\]", text_output, re.DOTALL)
                if match:
                    json_str = match.group(0)
                else:
                    json_str = text_output

                analysis_json = json.loads(json_str)

                if not isinstance(analysis_json, list):
                    raise ValueError("Unexpected response format from AI.")

                # --- Calculate Sadhya Cleanliness Score ---
                total_percentage = sum([100 - d.get("percentage_remaining", 0) for d in analysis_json]) / len(analysis_json)
                score = round(total_percentage, 2)

                # --- Display Results ---
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.subheader("🍛 Leaf Analysis Results")
                    st.table(analysis_json)
                with col2:
                    st.subheader("🌟 Sadhya Score")
                    st.metric("Cleanliness", f"{score} %")
                    if score > 80:
                        st.success("💯 Perfect! Ammachi is smiling! 😍")
                    elif score > 50:
                        st.warning("🤨 Not bad, but Ammachi is watching...")
                    else:
                        st.error("😒 Ammachi is disappointed...")

                # --- Roast ---
                leftovers = [d for d in analysis_json if d.get("percentage_remaining", 0) > 20]

                if not leftovers:
                    st.success("✅ Clean plate! Ammachi is proud of you! 🎉")
                    st.balloons()
                else:
                    roast_prompt = ROAST_PROMPT_TEMPLATE.format(leftovers=json.dumps(leftovers))
                    roast_response = roast_model.generate_content(roast_prompt)
                    st.subheader("🔥 Ammachi’s Verdict")
                    st.warning(roast_response.text.strip())

            except json.JSONDecodeError:
                st.error("⚠️ Could not decode AI's response as JSON. Try again with a clearer image.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
