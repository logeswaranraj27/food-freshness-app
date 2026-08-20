import streamlit as st
from PIL import Image
import pandas as pd
from datetime import datetime

# Import modular platform utilities
from utils.ai_engine import (
    load_freshness_model,
    load_fruit_classifier,
    analyze_food_quality,
    crop_center_square
)
from utils.cloud_db import (
    log_scan_to_cloud,
    fetch_cloud_scan_history,
    create_image_thumbnail_b64,
    export_history_to_csv,
    export_history_to_json
)
from utils.business_logic import (
    calculate_dynamic_markdown,
    get_recipe_recommendation,
    generate_html_audit_report
)
from utils.ui_components import (
    inject_custom_css,
    render_header,
    render_freshness_gauge,
    render_timeline_card,
    render_sensory_breakdown,
    render_analytics_dashboard
)
from utils.auth import render_auth_page

# ===== PAGE CONFIGURATION =====
st.set_page_config(
    page_title="FreshScan AI | Smart Retail & Quality Platform",
    page_icon="🍏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject modern glassmorphic theme styling
inject_custom_css()

# ===== SESSION STATE INITIALIZATION =====
if "user_logged_in" not in st.session_state:
    st.session_state["user_logged_in"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = "Customer"
if "user_name" not in st.session_state:
    st.session_state["user_name"] = "Guest"
if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""
if "store_name" not in st.session_state:
    st.session_state["store_name"] = ""
if "storage_temp_c" not in st.session_state:
    st.session_state["storage_temp_c"] = 22
if "currency_symbol" not in st.session_state:
    st.session_state["currency_symbol"] = "$"
if "current_analysis" not in st.session_state:
    st.session_state["current_analysis"] = None
if "last_image_uploaded" not in st.session_state:
    st.session_state["last_image_uploaded"] = None

# ===== AUTHENTICATION GATE =====
# If user is not logged in, show the Login/Signup portal and stop execution
if not st.session_state["user_logged_in"]:
    render_auth_page()
    st.stop()

# ===== LOAD AI MODELS =====
freshness_model = load_freshness_model()
classifier_model = load_fruit_classifier()

# ===== SIDEBAR: PROFILE, ROLE SWITCHER & SETTINGS =====
with st.sidebar:
    st.markdown("### 👤 User Profile")
    col_p1, col_p2 = st.columns([1, 3])
    with col_p1:
        st.markdown(
            '<div style="font-size: 28px; background: rgba(255,255,255,0.1); border-radius: 50%; text-align: center; line-height: 44px; width: 44px; height: 44px;">🧑‍💼</div>',
            unsafe_allow_html=True
        )
    with col_p2:
        st.markdown(f"**{st.session_state['user_name']}**")
        st.caption(f"{st.session_state['user_email']}")
        st.caption(f"Role: **{st.session_state['user_role']}**")

    # Role Selector
    st.markdown("---")
    st.markdown("#### 🔄 Portal Persona")
    selected_role = st.radio(
        "Select Portal Persona",
        ["🛒 Customer (Shopper)", "🏪 Seller (Retail Store)"],
        index=0 if st.session_state["user_role"] == "Customer" else 1,
        label_visibility="collapsed"
    )
    new_role = "Customer" if "Customer" in selected_role else "Seller"
    if new_role != st.session_state["user_role"]:
        st.session_state["user_role"] = new_role
        st.rerun()

    # Context Guidance
    if st.session_state["user_role"] == "Customer":
        st.info("💡 **Customer Mode**: Produce freshness check, safety ratings, ripeness days & zero-waste recipes.")
    else:
        st.success("💡 **Seller Mode**: Batch quality audit, dynamic markdown pricing & loss prevention.")

    # Settings Accordion
    with st.expander("⚙️ App & Storage Settings", expanded=False):
        st.session_state["storage_temp_c"] = st.slider(
            "Ambient Storage Temp (°C)",
            min_value=2,
            max_value=35,
            value=st.session_state["storage_temp_c"],
            help="Temperature directly impacts the calculated days until spoilage."
        )
        if st.session_state["storage_temp_c"] <= 6:
            st.caption("🧊 Refrigerator Crisper Mode (Preserves up to 2.5x longer)")
        elif st.session_state["storage_temp_c"] <= 18:
            st.caption("🍃 Cool Pantry / Cellar Storage")
        else:
            st.caption("☀️ Ambient Room Temperature")

        st.session_state["currency_symbol"] = st.selectbox(
            "Preferred Currency",
            ["$", "₹", "€", "£", "¥"],
            index=0
        )

    st.markdown("---")
    if st.button("🚪 Sign Out / Switch Account", use_container_width=True):
        st.session_state["user_logged_in"] = False
        st.session_state["user_name"] = "Guest"
        st.session_state["user_email"] = ""
        st.session_state["current_analysis"] = None
        st.rerun()

    st.markdown(
        """
        <div style="font-size: 11px; color: #94a3b8; text-align: center; margin-top: 16px;">
            <p>🟢 Cloud Database Connected</p>
            <p>© 2026 FreshScan AI Platform</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ===== MAIN HEADER =====
render_header(st.session_state["user_role"], st.session_state["user_name"])

# ===== MAIN TABS =====
tab1, tab2, tab3 = st.tabs([
    "🔍 AI Freshness Scanner",
    "📊 Executive Analytics & Metrics",
    "📋 Cloud Scan Logs & Export"
])

# =========================================================================
# TAB 1: AI FRESHNESS SCANNER & QUALITY ASSESSMENT
# =========================================================================
with tab1:
    col_input, col_results = st.columns([1, 1.4], gap="large")

    with col_input:
        st.markdown("### 📸 Fruit Input & Capture")
        scan_mode = st.radio(
            "Image Source",
            ["📤 Upload Photo", "📷 Live Camera Capture"],
            horizontal=True,
            label_visibility="collapsed"
        )

        image_to_process = None

        if "Upload" in scan_mode:
            uploaded_file = st.file_uploader(
                "Upload a high-resolution photo of the fruit...",
                type=["jpg", "jpeg", "png", "webp"]
            )
            if uploaded_file is not None:
                image_to_process = Image.open(uploaded_file).convert("RGB")
        else:
            camera_photo = st.camera_input("Capture fruit photo via camera")
            if camera_photo is not None:
                image_to_process = Image.open(camera_photo).convert("RGB")
                image_to_process = crop_center_square(image_to_process)

        if image_to_process is not None:
            st.image(image_to_process, caption="Selected Produce Image", use_container_width=True)

            # Store in session state
            st.session_state["last_image_uploaded"] = image_to_process

            # Seller batch pricing configuration
            seller_base_price = 3.50
            batch_id = "BATCH-2026-A1"
            if st.session_state["user_role"] == "Seller":
                c_b1, c_b2 = st.columns(2)
                with c_b1:
                    seller_base_price = st.number_input(
                        f"Base Price ({st.session_state['currency_symbol']})",
                        min_value=0.5,
                        value=3.50,
                        step=0.5
                    )
                with c_b2:
                    batch_id = st.text_input("Lot / Batch ID", value="BATCH-2026-A1")

            # Run Analysis Button
            analyze_btn = st.button("⚡ Run AI Deep Quality Analysis", type="primary", use_container_width=True)

            if analyze_btn:
                with st.spinner("🧠 AI identifying fruit variety, evaluating freshness & decay rates..."):
                    result = analyze_food_quality(
                        image=image_to_process,
                        freshness_model=freshness_model,
                        classifier_model=classifier_model,
                        storage_temp_c=st.session_state["storage_temp_c"]
                    )
                    st.session_state["current_analysis"] = result

                    # Automatically log scan to cloud database
                    thumbnail_b64 = create_image_thumbnail_b64(image_to_process)
                    markdown_data = calculate_dynamic_markdown(
                        freshness_score=result["freshness_score"],
                        base_price=seller_base_price,
                        currency_symbol=st.session_state["currency_symbol"]
                    )

                    log_payload = {
                        "fruit_name": result["fruit_name"],
                        "emoji": result["emoji"],
                        "label": result["status_label"],
                        "freshness_score": result["freshness_score"],
                        "confidence": result["confidence"],
                        "ripeness_stage": result["ripeness_stage"],
                        "days_to_ripe": result["days_to_ripe"],
                        "days_to_rot": result["days_to_rot"],
                        "user_role": st.session_state["user_role"],
                        "suggested_discount": markdown_data["discount_badge"],
                        "batch_id": batch_id,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "thumbnail_b64": thumbnail_b64
                    }
                    log_scan_to_cloud(log_payload)
                    st.success("✅ Analysis Complete & Synced to Cloud Database!")

    with col_results:
        st.markdown("### 🔬 AI Quality Assessment & Intelligence")

        if st.session_state["current_analysis"] is None:
            st.markdown(
                """
                <div class="glass-card" style="text-align: center; padding: 50px 20px;">
                    <div style="font-size: 48px; margin-bottom: 12px;">🍎 🍌 🍊</div>
                    <h3 style="color: #cbd5e1; margin-bottom: 8px;">Awaiting Produce Scan</h3>
                    <p style="color: #94a3b8; max-width: 450px; margin: 0 auto; font-size: 14px;">
                        Upload or snap a photo of any fruit on the left to reveal its variety, ripeness stage, freshness score, days until spoilage, and zero-waste / pricing recommendations.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            res = st.session_state["current_analysis"]

            # Top Fruit Title Banner
            st.markdown(
                f"""
                <div class="glass-card" style="border-left: 5px solid {'#10b981' if res['status_label'] == 'Fresh' else '#ef4444'};">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div>
                            <h2 style="margin: 0; font-size: 24px;">{res['emoji']} {res['fruit_name']}</h2>
                            <p style="margin: 2px 0 0 0; color: #94a3b8; font-size: 13px;">{res['category']} &bull; AI Confidence: <strong>{res['confidence']}%</strong></p>
                        </div>
                        <div style="text-align: right;">
                            <span style="background: {'rgba(16, 185, 129, 0.2)' if res['status_label'] == 'Fresh' else 'rgba(239, 68, 68, 0.2)'}; color: {'#34d399' if res['status_label'] == 'Fresh' else '#f87171'}; border: 1px solid {'#10b981' if res['status_label'] == 'Fresh' else '#ef4444'}; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 14px;">
                                {'✅ Fresh Produce' if res['status_label'] == 'Fresh' else '⚠️ Spoilage Detected'}
                            </span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Gauge & Summary Row
            col_g1, col_g2 = st.columns([1.2, 1])
            with col_g1:
                gauge_fig = render_freshness_gauge(res["freshness_score"], res["status_label"])
                st.plotly_chart(gauge_fig, use_container_width=True)

            with col_g2:
                st.markdown(
                    f"""
                    <div class="glass-card" style="height: 220px; display: flex; flex-direction: column; justify-content: center;">
                        <div style="font-size: 12px; color: #94a3b8; text-transform: uppercase;">Consumer Safety Rating</div>
                        <div style="font-size: 18px; font-weight: 800; color: {'#34d399' if res['safety_score'] >= 4 else ('#fbbf24' if res['safety_score'] >= 3 else '#f87171')}; margin: 4px 0;">
                            {'★' * res['safety_score'] + '☆' * (5 - res['safety_score'])} {res['safety_status']}
                        </div>
                        <hr style="border-color: rgba(255,255,255,0.1); margin: 8px 0;">
                        <div style="font-size: 12px; color: #94a3b8; text-transform: uppercase;">Buy / Keep Recommendation</div>
                        <div style="font-size: 14px; font-weight: 600; color: #f1f5f9; margin-top: 4px;">
                            {res['buy_recommendation']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Timeline Card
            render_timeline_card(
                days_to_ripe=res["days_to_ripe"],
                days_to_rot=res["days_to_rot"],
                ripeness_stage=res["ripeness_stage"],
                safety_status=res["safety_status"]
            )

            # Role-Specific Feature Block
            if st.session_state["user_role"] == "Customer":
                # Zero-Waste Culinary Guide
                recipe = get_recipe_recommendation(res["fruit_name"], res["ripeness_stage"])
                st.markdown(
                    f"""
                    <div class="glass-card" style="border-left: 4px solid #38bdf8;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <h4 style="margin: 0; color: #38bdf8; font-size: 16px;">👨‍🍳 Zero-Waste Culinary Assistant</h4>
                            <span style="font-size: 12px; background: rgba(56, 189, 248, 0.2); color: #38bdf8; padding: 2px 8px; border-radius: 10px;">⏱️ {recipe.get('time', '15 mins')}</span>
                        </div>
                        <div style="font-size: 15px; font-weight: 700; color: #f8fafc; margin-bottom: 4px;">{recipe.get('title', 'Delicious Fresh Recipe')}</div>
                        <p style="font-size: 13px; color: #cbd5e1; margin: 0;">{recipe.get('desc', 'Enjoy fresh or incorporate into healthy meal prep.')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                # Seller Dynamic Pricing Engine
                pricing = calculate_dynamic_markdown(
                    freshness_score=res["freshness_score"],
                    base_price=3.50,
                    currency_symbol=st.session_state["currency_symbol"]
                )
                st.markdown(
                    f"""
                    <div class="glass-card" style="border-left: 4px solid {pricing['badge_color']};">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <h4 style="margin: 0; color: #10b981; font-size: 16px;">🏷️ Dynamic Markdown & Pricing Engine</h4>
                            <span style="font-size: 13px; font-weight: bold; background: {pricing['badge_color']}; color: #ffffff; padding: 2px 10px; border-radius: 12px;">
                                {pricing['discount_badge']}
                            </span>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 8px;">
                            <div>
                                <span style="font-size: 12px; color: #94a3b8;">Original Price:</span>
                                <strong style="color: #cbd5e1; font-size: 15px;"> {pricing['original_price']}</strong>
                            </div>
                            <div>
                                <span style="font-size: 12px; color: #94a3b8;">Target Clearance Price:</span>
                                <strong style="color: #34d399; font-size: 16px;"> {pricing['suggested_price']}</strong>
                            </div>
                        </div>
                        <p style="font-size: 13px; color: #94a3b8; margin: 0;">
                            Strategy: <strong style="color: #f1f5f9;">{pricing['strategy']}</strong>
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Sensory and Nutritional Profile Expander
            with st.expander("🔬 View Detailed Sensory & Nutritional Profile", expanded=False):
                render_sensory_breakdown(res)

# =========================================================================
# TAB 2: EXECUTIVE ANALYTICS & METRICS
# =========================================================================
with tab2:
    st.markdown("### 📊 Executive Store & Spoilage Intelligence")
    history_data = fetch_cloud_scan_history(limit=100)

    if not history_data:
        st.info("No scan history found yet. Upload or capture fruits in the scanner tab to generate real-time cloud analytics.")
    else:
        render_analytics_dashboard(history_data)

# =========================================================================
# TAB 3: CLOUD SCAN LOGS & DATA EXPORT HUB
# =========================================================================
with tab3:
    st.markdown("### 📋 Cloud Data Log & Export Hub")

    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns([1, 1, 1.2, 1])

    history_records = fetch_cloud_scan_history(limit=50)

    with col_btn1:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

    with col_btn2:
        csv_data = export_history_to_csv(history_records)
        st.download_button(
            label="📥 Export CSV",
            data=csv_data,
            file_name=f"freshness_scans_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_btn3:
        json_data = export_history_to_json(history_records)
        st.download_button(
            label="📥 Export JSON",
            data=json_data,
            file_name=f"freshness_scans_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )

    with col_btn4:
        html_report = generate_html_audit_report(history_records, store_name="FreshScan SuperStore", inspector_name=st.session_state["user_name"])
        st.download_button(
            label="📄 Inspection Audit Report",
            data=html_report,
            file_name=f"food_quality_audit_{datetime.now().strftime('%Y%m%d')}.html",
            mime="text/html",
            use_container_width=True
        )

    st.markdown("---")

    # Render Visual Table with Image Thumbnail Previews
    if not history_records:
        st.write("No scan records logged yet.")
    else:
        st.markdown("#### 🖼️ Live Visual Inspection Log")

        # Display rich cards for each log item
        for r in history_records[:25]:
            thumb = r.get("thumbnail_b64", "")
            img_tag = (
                f'<img src="{thumb}" style="width: 54px; height: 54px; object-fit: cover; border-radius: 8px; border: 1px solid rgba(255,255,255,0.15);" />'
                if thumb
                else '<div style="width: 54px; height: 54px; background: rgba(255,255,255,0.1); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 24px;">🍎</div>'
            )

            is_fresh = r.get("label") == "Fresh"
            status_color = "#34d399" if is_fresh else "#f87171"
            card_html = f"""
            <div class="glass-card" style="padding: 12px 18px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
                <div style="display: flex; align-items: center; gap: 16px;">
                    {img_tag}
                    <div>
                        <div style="font-size: 16px; font-weight: 700; color: #f8fafc;">
                            {r.get('emoji', '🍎')} {r.get('fruit_name', 'Fruit')} 
                            <span style="font-size: 12px; color: {status_color}; margin-left: 8px; border: 1px solid {status_color}; padding: 2px 8px; border-radius: 12px;">
                                {r.get('label', 'N/A')} ({r.get('confidence', 95)}% conf)
                            </span>
                        </div>
                        <div style="font-size: 12px; color: #94a3b8; margin-top: 2px;">
                            Timestamp: {r.get('timestamp', 'N/A')} &bull; User: {r.get('user_role', 'Customer')} &bull; Stage: {r.get('ripeness_stage', 'Fresh')}
                        </div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 20px; text-align: right;">
                    <div>
                        <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">Freshness Score</div>
                        <div style="font-size: 16px; font-weight: 700; color: {'#34d399' if is_fresh else '#f87171'};">{r.get('freshness_score', 0)}%</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">Days to Rot</div>
                        <div style="font-size: 16px; font-weight: 700; color: {'#34d399' if r.get('days_to_rot', 0) >= 3 else '#f87171'};">{r.get('days_to_rot', 0)} days</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">Pricing Strategy</div>
                        <div style="font-size: 14px; font-weight: 700; color: #38bdf8;">{r.get('suggested_discount', '0%')}</div>
                    </div>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)