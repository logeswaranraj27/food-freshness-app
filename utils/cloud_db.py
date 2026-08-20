import requests
import json
import base64
import io
from datetime import datetime
from PIL import Image
import pandas as pd
import streamlit as st

FIREBASE_URL = "https://food-freshness-5f0c6-default-rtdb.asia-southeast1.firebasedatabase.app"
LOCAL_CACHE_KEY = "local_scan_history"


def create_image_thumbnail_b64(image: Image.Image, size=(80, 80)) -> str:
    """Generates a compressed base64 JPEG thumbnail data URI for UI rendering."""
    try:
        thumb = image.copy()
        thumb.thumbnail(size, Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        thumb.save(buffer, format="JPEG", quality=70)
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{encoded}"
    except Exception:
        return ""


def normalize_record(r: dict) -> dict:
    """Sanitizes and normalizes legacy or new records so no values display as 0% incorrectly."""
    label = r.get("label", "Fresh")
    try:
        conf = float(r.get("confidence", 90.0))
    except Exception:
        conf = 90.0

    # Ensure freshness_score
    if "freshness_score" in r and r["freshness_score"] is not None:
        try:
            freshness_score = round(float(r["freshness_score"]), 1)
        except Exception:
            freshness_score = 85.0
    else:
        if label == "Fresh":
            freshness_score = round(conf, 1)
        else:
            freshness_score = max(0.0, min(100.0, round(100.0 - conf, 1)))

    # Ensure days_to_rot
    if "days_to_rot" in r and r["days_to_rot"] is not None:
        try:
            days_to_rot = int(r["days_to_rot"])
        except Exception:
            days_to_rot = 0
    else:
        if label == "Fresh":
            days_to_rot = 5 if conf >= 85 else 3
        else:
            days_to_rot = 0

    fruit_name = r.get("fruit_name") or ("Fresh Produce" if label == "Fresh" else "Produce (Spoiled)")
    emoji = r.get("emoji") or ("🍏" if label == "Fresh" else "🥀")
    user_role = r.get("user_role") or "Customer"
    ripeness_stage = r.get("ripeness_stage") or ("Optimal Freshness" if label == "Fresh" else "Spoiled / Decayed")
    suggested_discount = r.get("suggested_discount") or ("0%" if label == "Fresh" else "100% OFF")

    return {
        "fruit_name": fruit_name,
        "emoji": emoji,
        "label": label,
        "freshness_score": freshness_score,
        "confidence": round(conf, 1),
        "ripeness_stage": ripeness_stage,
        "days_to_ripe": r.get("days_to_ripe", 0),
        "days_to_rot": days_to_rot,
        "user_role": user_role,
        "suggested_discount": suggested_discount,
        "batch_id": r.get("batch_id", "BATCH-001"),
        "timestamp": r.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "thumbnail_b64": r.get("thumbnail_b64", "")
    }


def log_scan_to_cloud(scan_record: dict) -> bool:
    """Logs a scan record to Firebase Realtime Database with local cache backup."""
    clean_record = normalize_record(scan_record)

    if LOCAL_CACHE_KEY not in st.session_state:
        st.session_state[LOCAL_CACHE_KEY] = []
    
    st.session_state[LOCAL_CACHE_KEY].insert(0, clean_record)

    try:
        res = requests.post(f"{FIREBASE_URL}/scans.json", json=clean_record, timeout=4)
        return res.status_code in [200, 201]
    except Exception:
        return True


def fetch_cloud_scan_history(limit: int = 50) -> list:
    """Fetches scan history from Firebase RTDB with fallback to local session state."""
    records = []
    try:
        res = requests.get(f"{FIREBASE_URL}/scans.json", timeout=4)
        if res.status_code == 200 and res.json():
            data = res.json()
            raw_list = list(data.values())
            raw_list.reverse()
            records = [normalize_record(r) for r in raw_list]
    except Exception:
        pass

    # Merge or fallback with session state records
    if LOCAL_CACHE_KEY in st.session_state and st.session_state[LOCAL_CACHE_KEY]:
        local_records = [normalize_record(r) for r in st.session_state[LOCAL_CACHE_KEY]]
        combined = []
        seen_timestamps = set()
        for r in local_records + records:
            ts = r.get("timestamp")
            if ts and ts not in seen_timestamps:
                seen_timestamps.add(ts)
                combined.append(r)
        return combined[:limit]

    return records[:limit]


def export_history_to_csv(history: list) -> str:
    """Converts history records to clean CSV string for export."""
    if not history:
        return "timestamp,fruit_name,label,freshness_score,confidence,ripeness_stage,days_to_rot,user_role,suggested_discount,batch_id\n"
    
    clean_rows = []
    for r in history:
        norm = normalize_record(r)
        clean_rows.append({
            "Timestamp": norm.get("timestamp", ""),
            "Fruit": norm.get("fruit_name", "Produce"),
            "Status": norm.get("label", ""),
            "Freshness (%)": norm.get("freshness_score", ""),
            "Confidence (%)": norm.get("confidence", ""),
            "Ripeness Stage": norm.get("ripeness_stage", ""),
            "Days to Rot": norm.get("days_to_rot", ""),
            "User Role": norm.get("user_role", ""),
            "Suggested Markdown": norm.get("suggested_discount", "0%"),
            "Batch ID": norm.get("batch_id", "")
        })
    df = pd.DataFrame(clean_rows)
    return df.to_csv(index=False)


def export_history_to_json(history: list) -> str:
    """Converts history records to formatted JSON string."""
    clean_history = []
    for r in history:
        norm = normalize_record(r)
        item = {k: v for k, v in norm.items() if k != "thumbnail_b64"}
        clean_history.append(item)
    return json.dumps(clean_history, indent=2)
