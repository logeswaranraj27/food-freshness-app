import streamlit as st
import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image
import numpy as np
import requests
from datetime import datetime

# ===== CONFIG =====
FIREBASE_URL = "https://food-freshness-5f0c6-default-rtdb.asia-southeast1.firebasedatabase.app"

st.set_page_config(page_title="Food Freshness Detector", page_icon="🍎", layout="wide")

@st.cache_resource
def load_model():
    return tf.keras.models.load_model("freshness_model.h5")

model = load_model('./model_name.h5')

# ===== HELPER FUNCTIONS =====

def predict_freshness(image):
    img_resized = image.resize((224, 224))
    img_array = img_to_array(img_resized) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    prediction = model.predict(img_array)[0][0]

    if prediction < 0.5:
        label = "Fresh"
        confidence = (1 - prediction) * 100
        shelf_life = estimate_shelf_life(confidence)
    else:
        label = "Rotten"
        confidence = prediction * 100
        shelf_life = "Already spoiled — discard"

    return label, confidence, shelf_life


def crop_center_square(image):
    width, height = image.size
    min_dim = min(width, height)
    left = (width - min_dim) / 2
    top = (height - min_dim) / 2
    right = (width + min_dim) / 2
    bottom = (height + min_dim) / 2
    return image.crop((left, top, right, bottom))


def estimate_shelf_life(confidence):
    # Simple heuristic: higher confidence in "Fresh" = longer estimated shelf life
    if confidence >= 90:
        return "4-6 days"
    elif confidence >= 75:
        return "2-3 days"
    elif confidence >= 60:
        return "1-2 days"
    else:
        return "Use today"


def log_to_cloud(label, confidence, shelf_life):
    try:
        data = {
            "label": label,
            "confidence": round(float(confidence), 2),
            "shelf_life": shelf_life,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        requests.post(f"{FIREBASE_URL}/scans.json", json=data, timeout=5)
        return True
    except Exception as e:
        st.warning(f"Cloud logging failed: {e}")
        return False


def get_scan_history():
    try:
        response = requests.get(f"{FIREBASE_URL}/scans.json", timeout=5)
        data = response.json()
        if data is None:
            return []
        # Firebase returns a dict of {key: record} — convert to list, most recent first
        records = list(data.values())
        records.reverse()
        return records
    except Exception as e:
        st.warning(f"Could not load history: {e}")
        return []


def show_result(image, label, confidence, shelf_life):
    st.image(image, caption="Scanned Image", use_container_width=True)
    if label == "Fresh":
        st.success(f"✅ {label} — {confidence:.2f}% confidence")
        st.info(f"🕒 Estimated shelf life: **{shelf_life}**")
    else:
        st.error(f"⚠️ {label} — {confidence:.2f}% confidence")
        st.info(f"🕒 {shelf_life}")


# ===== UI =====

st.title("🍎 AI Food Freshness Detector — Smart Retail Dashboard")
st.write("For shopkeepers and customers to instantly check fruit quality using AI, with results logged to the cloud in real time.")

tab1, tab2, tab3 = st.tabs(["📤 Upload Photo", "📷 Live Camera", "📊 Scan History (Cloud Dashboard)"])

with tab1:
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        label, confidence, shelf_life = predict_freshness(image)
        show_result(image, label, confidence, shelf_life)
        log_to_cloud(label, confidence, shelf_life)

with tab2:
    camera_photo = st.camera_input("Take a photo of the fruit")
    if camera_photo is not None:
        image = Image.open(camera_photo).convert("RGB")
        image = crop_center_square(image)
        label, confidence, shelf_life = predict_freshness(image)
        show_result(image, label, confidence, shelf_life)
        log_to_cloud(label, confidence, shelf_life)

with tab3:
    st.subheader("Recent Scans (pulled live from cloud database)")
    if st.button("🔄 Refresh"):
        st.rerun()

    history = get_scan_history()
    if len(history) == 0:
        st.write("No scans yet — try uploading or scanning a fruit first.")
    else:
        st.dataframe(history, use_container_width=True)

        fresh_count = sum(1 for r in history if r.get("label") == "Fresh")
        rotten_count = sum(1 for r in history if r.get("label") == "Rotten")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Scans", len(history))
        col2.metric("Fresh", fresh_count)
        col3.metric("Rotten", rotten_count)