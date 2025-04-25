import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil import parser
from auth_rest import sign_up, sign_in
from auth import check_session
from firebase_utils import save_submission, has_valid_submission, get_all_submissions

# --- Page Configuration ---
st.set_page_config(layout="wide")
st.title("Experiment Submission & Tracker")

# --- Initialize Session State ---
if "id_token" not in st.session_state:
    st.session_state["id_token"] = None
if "email" not in st.session_state:
    st.session_state["email"] = ""
if "just_submitted" not in st.session_state:
    st.session_state["just_submitted"] = False

# --- Sidebar: Login / Signup ---
with st.sidebar:
    st.header("Login / Sign Up")
    email_input = st.text_input("Email", key="login_email")
    password_input = st.text_input("Password", type="password", key="login_password")

    col1, col2 = st.columns(2)

    # Login Button 
    with col1:
        if st.button("Login"):
            if email_input and password_input:
                resp = sign_in(email_input, password_input)
                if isinstance(resp, dict) and "idToken" in resp:
                    st.session_state["id_token"] = resp["idToken"]
                    st.session_state["email"] = email_input
                    st.session_state["just_submitted"] = False 
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    error_message = (resp.get("error", {}).get("message", "Login failed")
                                     if isinstance(resp, dict) else str(resp))
                    st.error(f"Login failed: {error_message}")
            else:
                st.warning("Please enter both email and password.")

    # Sign Up Button 
    with col2:
        if st.button("Sign Up"):
            if email_input and password_input:
                resp = sign_up(email_input, password_input)
                if isinstance(resp, dict) and "idToken" in resp:
                    st.success("Signed up! Please login now.")
                else:
                    error_message = str(resp) if resp else "Signup failed"
                    st.error(f"Signup failed: {error_message}")
            else:
                st.warning("Please enter both email and password.")

# --- Main Content Area ---

if st.session_state.get("id_token"):
    user_info = check_session(st.session_state["id_token"])

    if user_info:
        email = st.session_state["email"]
        st.success(f"Welcome {email}!")
        valid_access = False
        if st.session_state.get("just_submitted", False):
             valid_access = True
             st.session_state["just_submitted"] = False 
        else:
             valid_access = has_valid_submission(email)

        show_submission_form = False
        if valid_access:
            st.success("You have access to the experiment log.")
            show_submission_form = st.checkbox("Submit another experiment", key="submit_another_cb")
        else:
            st.warning("You don’t currently have access to the experiment log. Please submit a new experiment.")
            show_submission_form = True 

        # --- Submission Form ---
        if show_submission_form:
            st.subheader("Submit a New Experiment")
            with st.form("submission_form", clear_on_submit=True):
                experiment_name = st.text_input("Experiment Name (e.g. CNN-v1)", key="exp_name")
                experiment_type = st.selectbox("Experiment Type", ["Classification", "Regression", "Clustering", "Other"], key="exp_type")
                data_source = st.selectbox("Data Source", ["Kaggle", "Internal Dataset", "Simulated", "Other"], key="exp_data")
                parameters = st.text_area("Key Parameters (e.g. model type, hyperparams)", key="exp_params")
                results = st.text_area("Results Summary (e.g. accuracy, loss)", key="exp_results")
                status = st.selectbox("Status", ["Success", "Failed", "In Progress"], key="exp_status")
                notes = st.text_area("Extra Notes (optional)", key="exp_notes")

                # Form submission 
                submitted = st.form_submit_button("Submit Experiment")

                if submitted:
                    if not (experiment_name and parameters and results):
                        st.error("Please fill in required fields: Experiment Name, Key Parameters, and Results Summary.")
                    else:
                        submission_data = {
                            "email": email,
                            "experiment_name": experiment_name,
                            "experiment_type": experiment_type,
                            "data_source": data_source,
                            "parameters": parameters,
                            "results": results,
                            "status": status,
                            "notes": notes or "N/A",
                            "submitted_at": datetime.now(datetime.UTC).isoformat() + "Z"
                        }
                        save_submission(email, submission_data)
                        st.success("Thanks! Your experiment was submitted.")
                        st.session_state["just_submitted"] = True
                        st.rerun()

        # --- Display Area (Show only if user has valid access) ---
        if valid_access:
            st.divider()
            st.subheader("View Submitted Experiments")
            submissions = [] 
            with st.spinner("Loading experiments..."):
                submissions = get_all_submissions()

            if submissions:
                processed_entries = []

                def get_sort_key(entry_dict):
                    ts_str = entry_dict.get("submitted_at", "")
                    try:
                        if ts_str.endswith('Z'): 
                           ts_str = ts_str[:-1] + '+00:00'
                        return parser.isoparse(ts_str)
                    except (TypeError, ValueError):
                        return datetime.min 
                submissions = sorted(submissions, key=get_sort_key, reverse=True)


                for entry in submissions:
                    submitted_at_str = "Invalid Date" 
                    ts_str = entry.get("submitted_at")
                    if ts_str:
                       try:
                           if ts_str.endswith('Z'):
                               ts_str = ts_str[:-1] + '+00:00'
                           submitted_dt = parser.isoparse(ts_str)
                           submitted_at_str = submitted_dt.strftime("%Y-%m-%d %H:%M UTC")
                       except (TypeError, ValueError):
                           submitted_at_str = entry.get("submitted_at", "N/A") # Fallback

                    processed_entries.append({
                        "Experiment": entry.get("experiment_name", "N/A"),
                        "Type": entry.get("experiment_type", "N/A"),
                        "Data Source": entry.get("data_source", "N/A"),
                        "Status": entry.get("status", "N/A"),
                        "Submitted At": submitted_at_str,
                        "Submitted By": entry.get("submitted_by", "N/A"),
                    })

                df = pd.DataFrame(processed_entries)
                st.dataframe(df, use_container_width=True)

            else:
                st.info("The experiment log is currently empty.")

    else:
        st.error("Session invalid or expired. Please login again.")
        st.session_state["id_token"] = None
        st.session_state["email"] = ""
        st.session_state["just_submitted"] = False
        st.rerun()

elif not st.session_state.get("id_token"):
    st.session_state["just_submitted"] = False
    st.info("Please login or sign up using the sidebar to submit or view experiments.")

