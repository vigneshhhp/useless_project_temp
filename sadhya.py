import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# --- Configuration ---
# Store your API key in st.secrets for deployment
# For local development, you can paste it here directly
# genai.configure(api_key="YOUR_GOOGLE_AI_API_KEY")

genai.configure(api_key="AIzaSyAuqiRJ4tFih3VxrRW-ZA6VdTlsYwhJZOk")

try:
#     # You will use this part later when you deploy your app online
     genai.configure(api_key=st.secrets["AIzaSyAuqiRJ4tFih3VxrRW-ZA6VdTlsYwhJZOk"]) 
except Exception:
     st.error("Could not configure Gemini API. Please provide an API key.")


# --- Gemini Models ---
analyzer_model = genai.GenerativeModel('gemini-pro-vision')
roast_model = genai.GenerativeModel('gemini-pro')

# --- Prompts ---
ANALYSIS_PROMPT = """You are an expert in Keralite cuisine. Analyze the provided image of a Sadhya... (full prompt from above)"""
ROAST_PROMPT_TEMPLATE = """You are a witty and sarcastic Malayali Ammachi... Based on this, generate a funny roast: {leftovers}"""

# --- Streamlit UI ---
st.set_page_config(layout="wide", page_title="AI Sadhya Critic")
st.title("AI Sadhya Critic 🧐🍽️")
st.write("Upload a photo of your Sadhya plate (after you've eaten) and get a fair, unbiased judgment!")

uploaded_file = st.file_uploader("Choose a photo of your Sadhya leaf...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the image
    image = Image.open(uploaded_file)
    st.image(image, caption='Your Sadhya Plate', use_column_width=True)
    st.divider()

    if st.button('Analyze and Judge My Meal!', type="primary"):
        with st.spinner('Our expert Ammachi is inspecting your leaf...'):
            try:
                # 1. Analyze the Leaf
                response = analyzer_model.generate_content([ANALYSIS_PROMPT, image])
                
                # Clean the response to get pure JSON
                analysis_text = response.text.replace('```json', '').replace('```', '').strip()
                analysis_json = json.loads(analysis_text)
                
                st.subheader("Leaf Analysis Results:")
                st.json(analysis_json)

                # 2. Generate the Roast
                leftovers = [d for d in analysis_json if d.get('percentage_remaining', 0) > 20]
                
                if not leftovers:
                    st.balloons()
                    st.success("Clean plate! You have earned the Ammachi's respect. Well done!")
                else:
                    roast_prompt = ROAST_PROMPT_TEMPLATE.format(leftovers=json.dumps(leftovers))
                    roast_response = roast_model.generate_content(roast_prompt)
                    
                    st.subheader("The Verdict... 🥁")
                    st.warning(f"**Ammachi says:** \"{roast_response.text}\"")

            except json.JSONDecodeError:
                st.error("AI returned an invalid analysis format. It might be confused by the image. Try another photo!")
            except Exception as e:
                st.error(f"An error occurred: {e}")