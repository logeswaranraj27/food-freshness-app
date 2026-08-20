import streamlit as st
import requests
import json
import hashlib

FIREBASE_USERS_URL = "https://food-freshness-5f0c6-default-rtdb.asia-southeast1.firebasedatabase.app/users.json"

# In-memory default users for instant out-of-the-box demo & fallback
DEFAULT_USERS = {
    "customer@freshscan.io": {
        "name": "Sarah Miller",
        "password_hash": hashlib.sha256("password123".encode()).hexdigest(),
        "role": "Customer",
        "store": "Smart Consumer"
    },
    "seller@freshmart.com": {
        "name": "Marcus Vance",
        "password_hash": hashlib.sha256("password123".encode()).hexdigest(),
        "role": "Seller",
        "store": "FreshMart Supermarket #104"
    }
}


def hash_password(password: str) -> str:
    """Returns SHA256 hashed password string."""
    return hashlib.sha256(password.encode()).hexdigest()


def get_all_users() -> dict:
    """Fetches users from Firebase with fallback to local defaults."""
    users = dict(DEFAULT_USERS)
    try:
        res = requests.get(FIREBASE_USERS_URL, timeout=3)
        if res.status_code == 200 and res.json():
            db_users = res.json()
            for k, u in db_users.items():
                if isinstance(u, dict) and "email" in u:
                    users[u["email"].lower()] = u
    except Exception:
        pass
    return users


def authenticate_user(email: str, password: str):
    """Authenticates email and password. Returns (bool, user_dict)."""
    email_clean = email.strip().lower()
    users = get_all_users()

    if email_clean in users:
        user = users[email_clean]
        if user.get("password_hash") == hash_password(password):
            return True, user
    return False, None


def register_user(name: str, email: str, password: str, role: str, store_name: str = ""):
    """Registers a new user in Firebase and session state."""
    email_clean = email.strip().lower()
    users = get_all_users()

    if email_clean in users:
        return False, "An account with this email already exists."

    new_user = {
        "name": name.strip(),
        "email": email_clean,
        "password_hash": hash_password(password),
        "role": role,
        "store": store_name.strip() if store_name else ("Shopper" if role == "Customer" else "Retail Store")
    }

    # Save to Firebase
    try:
        requests.post(FIREBASE_USERS_URL, json=new_user, timeout=3)
    except Exception:
        pass

    # Save to default fallback
    DEFAULT_USERS[email_clean] = new_user
    return True, new_user


def render_auth_page():
    """Renders a sleek, dedicated Login / Registration gate before accessing the app."""
    st.markdown(
        """
        <style>
            .auth-container {
                max-width: 480px;
                margin: 40px auto;
                background: rgba(15, 23, 42, 0.75);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 20px;
                padding: 36px 32px;
                box-shadow: 0 20px 50px -15px rgba(0, 0, 0, 0.7);
            }
            .auth-logo {
                font-size: 42px;
                margin-bottom: 8px;
                text-align: center;
            }
            .auth-title {
                text-align: center;
                font-size: 26px;
                font-weight: 800;
                color: #ffffff;
                margin: 0 0 6px 0;
            }
            .auth-subtitle {
                text-align: center;
                font-size: 13px;
                color: #94a3b8;
                margin-bottom: 24px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 1.8, 1])

    with col2:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="font-size: 46px;">🍏 ✨</div>
                <h1 style="font-size: 28px; font-weight: 800; color: #ffffff; margin: 4px 0;">FreshScan AI Portal</h1>
                <p style="font-size: 14px; color: #94a3b8; margin: 0;">Cloud-Powered Produce Quality & Inventory Intelligence</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        auth_tab1, auth_tab2 = st.tabs(["🔑 Sign In", "📝 Create Account"])

        with auth_tab1:
            st.markdown("##### Welcome Back")
            login_email = st.text_input("Email Address", placeholder="e.g., customer@freshscan.io", key="login_email")
            login_password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pwd")

            if st.button("🚀 Sign In to Dashboard", type="primary", use_container_width=True):
                if not login_email or not login_password:
                    st.error("Please provide both email and password.")
                else:
                    success, user_data = authenticate_user(login_email, login_password)
                    if success:
                        st.session_state["user_logged_in"] = True
                        st.session_state["user_name"] = user_data.get("name", "User")
                        st.session_state["user_role"] = user_data.get("role", "Customer")
                        st.session_state["user_email"] = user_data.get("email", login_email)
                        st.session_state["store_name"] = user_data.get("store", "")
                        st.success(f"Welcome back, {st.session_state['user_name']}! Redirecting...")
                        st.rerun()
                    else:
                        st.error("Invalid email or password. Please check your credentials.")

            st.markdown("---")
            st.caption("⚡ **Instant One-Click Demo Access:**")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                if st.button("🛒 Demo as Customer", use_container_width=True):
                    st.session_state["user_logged_in"] = True
                    st.session_state["user_name"] = "Sarah Miller"
                    st.session_state["user_role"] = "Customer"
                    st.session_state["user_email"] = "customer@freshscan.io"
                    st.session_state["store_name"] = "Smart Consumer"
                    st.rerun()
            with col_d2:
                if st.button("🏪 Demo as Store Seller", use_container_width=True):
                    st.session_state["user_logged_in"] = True
                    st.session_state["user_name"] = "Marcus Vance"
                    st.session_state["user_role"] = "Seller"
                    st.session_state["user_email"] = "seller@freshmart.com"
                    st.session_state["store_name"] = "FreshMart Supermarket #104"
                    st.rerun()

        with auth_tab2:
            st.markdown("##### Register New Organization / User")
            reg_name = st.text_input("Full Name", placeholder="e.g., Alex Johnson", key="reg_name")
            reg_email = st.text_input("Email Address", placeholder="e.g., alex@company.com", key="reg_email")
            reg_role = st.selectbox("I am joining as:", ["🛒 Customer (Shopper / Consumer)", "🏪 Seller (Grocery / Retailer)"], key="reg_role")
            role_val = "Customer" if "Customer" in reg_role else "Seller"

            reg_store = ""
            if role_val == "Seller":
                reg_store = st.text_input("Store / Organization Name", placeholder="e.g., GreenGrocers Ltd.", key="reg_store")

            reg_pwd1 = st.text_input("Create Password", type="password", placeholder="At least 6 characters", key="reg_pwd1")
            reg_pwd2 = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="reg_pwd2")

            if st.button("✨ Create Account & Enter", type="primary", use_container_width=True):
                if not reg_name or not reg_email or not reg_pwd1:
                    st.error("Please fill in all required fields.")
                elif len(reg_pwd1) < 4:
                    st.error("Password must be at least 4 characters long.")
                elif reg_pwd1 != reg_pwd2:
                    st.error("Passwords do not match.")
                else:
                    success, res = register_user(reg_name, reg_email, reg_pwd1, role_val, reg_store)
                    if success:
                        st.session_state["user_logged_in"] = True
                        st.session_state["user_name"] = reg_name
                        st.session_state["user_role"] = role_val
                        st.session_state["user_email"] = reg_email
                        st.session_state["store_name"] = reg_store if reg_store else "Retailer"
                        st.success("Account created successfully! Logging in...")
                        st.rerun()
                    else:
                        st.error(res)
