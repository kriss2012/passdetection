import streamlit as st
import tensorflow as tf
import pickle
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
import os

# Page Config
st.set_page_config(page_title="PassNet AI", page_icon="🔐")

# Paths
MODEL_PATH = 'models/model.h5'
TOKENIZER_PATH = 'models/tokenizer.pickle'
MAX_LEN = 30

@st.cache_resource
def load_resources():
    """Load model and tokenizer only once to keep app fast"""
    if not os.path.exists(MODEL_PATH):
        return None, None
    
    model = tf.keras.models.load_model(MODEL_PATH)
    with open(TOKENIZER_PATH, 'rb') as handle:
        tokenizer = pickle.load(handle)
    return model, tokenizer

# UI Header
st.title("🔐 PassNet: Context-Aware Security")
st.markdown("This AI isn't just counting symbols. It was trained on **millions of real leaks** to detect human patterns.")

# Load AI
model, tokenizer = load_resources()

if model is None:
    st.error("Model not found! Please run 'train_model.py' first.")
else:
    # Input
    password = st.text_input("Test a password:", type="password")

    if password:
        # Preprocess
        seq = tokenizer.texts_to_sequences([password])
        padded = pad_sequences(seq, maxlen=MAX_LEN, padding='post')
        
        # Predict
        prediction = model.predict(padded)[0][0] # Returns 0.0 to 1.0
        
        # Logic for score
        score = prediction * 100
        
        st.write("---")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.metric(label="Safety Score", value=f"{score:.1f}/100")
            
        with col2:
            if score < 50:
                st.error(f"⚠️ **WEAK**: This follows common leak patterns.")
                st.progress(int(score))
            elif score < 80:
                st.warning(f"🛡️ **MODERATE**: Better, but could be stronger.")
                st.progress(int(score))
            else:
                st.success(f"🚀 **STRONG**: High entropy and non-standard pattern.")
                st.progress(int(score))

        # Advanced Analysis (Visuals)
        st.caption("AI Probability Analysis")
        # Visualizing the decision boundary (Optional visual flair)
        chart_data = {"Weak Probability": 100-score, "Strong Probability": score}
        st.bar_chart(chart_data)
        #.venv\Scripts\Activate.ps1