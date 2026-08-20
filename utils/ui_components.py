import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def inject_custom_css():
    """Injects high-end modern CSS with sleek glassmorphism and refined typography."""
    css = """
    <style>
        /* Import Modern Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Outfit', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Gradient Banner & Main Layout */
        .main-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #064e3b 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 24px 32px;
            margin-bottom: 24px;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
            color: #ffffff;
            position: relative;
            overflow: hidden;
        }

        .main-header::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -20%;
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(16, 185, 129, 0.25) 0%, rgba(0,0,0,0) 70%);
            pointer-events: none;
        }

        /* Glassmorphism Feature Cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 16px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .glass-card:hover {
            transform: translateY(-2px);
            border-color: rgba(16, 185, 129, 0.4);
            box-shadow: 0 12px 24px -10px rgba(16, 185, 129, 0.2);
        }

        /* Timeline Badge Cards */
        .timeline-card {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 14px 18px;
            border-radius: 12px;
            margin: 8px 0;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }

        /* Role Badges */
        .role-badge-customer {
            display: inline-block;
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: #ffffff;
            font-size: 12px;
            font-weight: 700;
            padding: 4px 12px;
            border-radius: 20px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        .role-badge-seller {
            display: inline-block;
            background: linear-gradient(135deg, #10b981 0%, #047857 100%);
            color: #ffffff;
            font-size: 12px;
            font-weight: 700;
            padding: 4px 12px;
            border-radius: 20px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        /* Sensory Pill Tags */
        .sensory-pill {
            display: inline-flex;
            align-items: center;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.12);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            margin: 4px 6px 4px 0;
        }

        /* Buttons Styling */
        div.stButton > button {
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.25s ease;
        }

        /* Metric block styling */
        [data-testid="stMetricValue"] {
            font-size: 28px !important;
            font-weight: 800 !important;
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.1);
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_header(user_role: str, user_name: str = "Guest"):
    """Renders the top branding and role indicator header."""
    is_seller = user_role == "Seller"
    badge_class = "role-badge-seller" if is_seller else "role-badge-customer"
    badge_text = "🏪 Store Inventory & Retail Mode" if is_seller else "🛒 Smart Consumer & Shopper Mode"
    sub_desc = (
        "Automated Produce Quality Control, Dynamic Markdown Engine & Batch Loss Prevention."
        if is_seller
        else "Instant AI Fruit Quality Check, Ripeness & Rot Timeline, and Zero-Waste Kitchen Guide."
    )

    header_html = f"""
    <div class="main-header">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <h1 style="margin: 0; font-size: 28px; font-weight: 800; display: flex; align-items: center; gap: 10px;">
                    🍏 FreshScan AI <span style="font-size: 18px; opacity: 0.8; font-weight: 400;">| Cloud Retail Platform</span>
                </h1>
                <p style="margin: 6px 0 0 0; font-size: 14px; color: #94a3b8;">
                    {sub_desc}
                </p>
            </div>
            <div style="text-align: right;">
                <span class="{badge_class}">{badge_text}</span>
                <p style="margin: 6px 0 0 0; font-size: 13px; color: #cbd5e1;">Logged in as: <strong>{user_name}</strong></p>
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


def render_freshness_gauge(freshness_score: float, status_label: str):
    """Creates a high-end radial gauge chart for Freshness Score."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=freshness_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "AI Freshness Index", 'font': {'size': 18, 'color': '#ffffff'}},
        number={'suffix': "%", 'font': {'size': 36, 'color': '#ffffff', 'family': 'Outfit'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#10b981" if status_label == "Fresh" else "#ef4444", 'thickness': 0.28},
            'bgcolor': "rgba(255,255,255,0.05)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 40], 'color': "rgba(239, 68, 68, 0.2)"},
                {'range': [40, 70], 'color': "rgba(245, 158, 11, 0.2)"},
                {'range': [70, 100], 'color': "rgba(16, 185, 129, 0.2)"}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 3},
                'thickness': 0.75,
                'value': freshness_score
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=35, b=20),
        height=220
    )
    return fig


def render_timeline_card(days_to_ripe: int, days_to_rot: int, ripeness_stage: str, safety_status: str):
    """Renders the interactive decay & ripeness timeline component."""
    card_html = f"""
    <div class="glass-card">
        <h4 style="margin: 0 0 12px 0; color: #38bdf8; font-size: 16px;">⏱️ AI Predictive Lifespan & Ripeness Timeline</h4>
        <div class="timeline-card">
            <div>
                <div style="font-size: 12px; color: #94a3b8; text-transform: uppercase;">Ripeness Stage</div>
                <div style="font-size: 16px; font-weight: 700; color: #f8fafc; margin-top: 2px;">{ripeness_stage}</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 12px; color: #94a3b8; text-transform: uppercase;">Days to Optimal Ripe</div>
                <div style="font-size: 20px; font-weight: 800; color: {'#38bdf8' if days_to_ripe > 0 else '#10b981'};">
                    {f"{days_to_ripe} Days" if days_to_ripe > 0 else "Ready Now ✅"}
                </div>
            </div>
        </div>
        <div class="timeline-card" style="border-left: 4px solid {'#10b981' if days_to_rot >= 3 else ('#f59e0b' if days_to_rot > 0 else '#ef4444')};">
            <div>
                <div style="font-size: 12px; color: #94a3b8; text-transform: uppercase;">Microbial Shelf-Life Window</div>
                <div style="font-size: 14px; color: #cbd5e1; margin-top: 2px;">{safety_status}</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 12px; color: #94a3b8; text-transform: uppercase;">Days until Spoilage</div>
                <div style="font-size: 22px; font-weight: 800; color: {'#10b981' if days_to_rot >= 3 else ('#f59e0b' if days_to_rot > 0 else '#ef4444')};">
                    {f"{days_to_rot} Days" if days_to_rot > 0 else "Expired ⚠️"}
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_sensory_breakdown(fruit_data: dict):
    """Renders the AI Sensory, Tactile & Nutritional Profile."""
    sensory = fruit_data.get("sensory", {})
    card_html = f"""
    <div class="glass-card">
        <h4 style="margin: 0 0 12px 0; color: #a78bfa; font-size: 16px;">🔬 AI Sensory Profile & Nutritional Breakdown</h4>
        <div style="margin-bottom: 10px;">
            <p style="margin: 4px 0; font-size: 14px;"><strong>👃 Aroma Signature:</strong> {sensory.get('aroma', 'Natural fresh fruit aroma')}</p>
            <p style="margin: 4px 0; font-size: 14px;"><strong>🖐️ Tactile Firmness:</strong> {sensory.get('firmness', 'Standard elasticity')}</p>
            <p style="margin: 4px 0; font-size: 14px;"><strong>👁️ Visual Indicators:</strong> {sensory.get('appearance', 'Clean uniform peel')}</p>
            <p style="margin: 4px 0; font-size: 14px;"><strong>🥗 Key Nutrients:</strong> {fruit_data.get('nutrients', 'Vitamins & Fiber')}</p>
            <p style="margin: 4px 0; font-size: 14px;"><strong>🌡️ Ideal Preservation:</strong> {fruit_data.get('optimal_temp', 'Cool storage')}</p>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_analytics_dashboard(history_records: list):
    """Renders interactive Plotly visual analytics for quality managers."""
    if not history_records:
        st.info("No scan records found. Perform some scans to unlock interactive cloud analytics.")
        return

    df = pd.DataFrame(history_records)

    # 1. Metric Overview Row
    total_scans = len(df)
    fresh_count = len(df[df["label"] == "Fresh"])
    rotten_count = len(df[df["label"] == "Rotten"])
    fresh_rate = round((fresh_count / total_scans) * 100, 1) if total_scans > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Total Inspected", f"{total_scans} units")
    col2.metric("✅ Quality Pass Rate", f"{fresh_rate}%")
    col3.metric("🍏 Fresh Items", f"{fresh_count}")
    col4.metric("⚠️ Spoilage Flagged", f"{rotten_count}")

    st.markdown("---")

    # 2. Charts Row
    c1, c2 = st.columns(2)

    with c1:
        # Pie / Donut distribution
        status_counts = df["label"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        colors = ["#10b981", "#ef4444"] if status_counts["Status"].iloc[0] == "Fresh" else ["#ef4444", "#10b981"]

        fig_pie = px.pie(
            status_counts,
            names="Status",
            values="Count",
            title="Fresh vs. Spoiled Ratio",
            hole=0.5,
            color="Status",
            color_discrete_map={"Fresh": "#10b981", "Rotten": "#ef4444"}
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#ffffff", family="Outfit"),
            margin=dict(t=40, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        # Fruit Variety Distribution
        if "fruit_name" in df.columns:
            fruit_counts = df["fruit_name"].value_counts().reset_index()
            fruit_counts.columns = ["Fruit", "Scans"]
            fig_bar = px.bar(
                fruit_counts.head(7),
                x="Fruit",
                y="Scans",
                title="Top Scanned Fruit Varieties",
                color="Scans",
                color_continuous_scale="Viridis"
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ffffff", family="Outfit"),
                margin=dict(t=40, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_bar, use_container_width=True)
