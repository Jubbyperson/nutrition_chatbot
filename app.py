# Main app ui

import streamlit as st
import os
from pathlib import Path
from db import get_user, get_logs, insert_log, insert_user, verify_password, init_db
from utils import validate_user_data, validate_log_data, ACTIVITY_LEVELS, GOALS
from logic import calculate_nutrition_profile
import bcrypt
from models.ai_coach import NutritionCoach
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

# Configure page - must be first Streamlit command
st.set_page_config(
    page_title="NutriChat - AI Nutrition Coach",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/nutrichat',
        'Report a bug': None,
        'About': 'NutriChat - Your AI Nutrition Coach'
    }
)

# Custom CSS for dark mode
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* All text elements */
    h1, h2, h3, h4, h5, h6, p, label, div, span {
        color: #FFFFFF !important;
    }
    
    /* Form labels */
    .stTextInput label, .stNumberInput label, .stSelectbox label {
        color: #FFFFFF !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #4A4A4A !important;
    }
    
    /* Card styling */
    .metric-card {
        background-color: #262730;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        border: 1px solid #3E3E3E;
        color: #FFFFFF;
    }
    
    /* Button styling - target all buttons including form submit buttons */
    .stButton>button,
    button[kind="primary"],
    div[data-testid="stButton"]>button,
    .stForm button[type="submit"],
    .stForm button[kind="secondaryFormSubmit"],
    .stForm button[data-testid="stFormSubmitButton"] {
        background-color: #FF0000 !important;  /* Red background */
        color: #FFFFFF !important;            /* White text */
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 4px !important;
        font-weight: 500 !important;
        transition: background-color 0.3s !important;
        width: 100% !important;
    }
    
    .stButton>button:hover,
    button[kind="primary"]:hover,
    div[data-testid="stButton"]>button:hover,
    .stForm button[type="submit"]:hover,
    .stForm button[kind="secondaryFormSubmit"]:hover,
    .stForm button[data-testid="stFormSubmitButton"]:hover {
        background-color: #CC0000 !important;  /* Darker red on hover */
    }
    
    /* Form styling */
    .stForm {
        background-color: #262730;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #3E3E3E;
        color: #FFFFFF;
    }
    
    /* Input fields - All inputs (text, number, select) */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stSelectbox>div>div[data-baseweb="select"] {
        background-color: #FFFFFF !important;  /* White background */
        color: #000000 !important;            /* Black text */
        border: 1px solid #3E3E3E !important;
    }
    
    /* Select box specific styling */
    .stSelectbox>div>div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;  /* White background */
        color: #000000 !important;            /* Black text */
    }
    
    /* Target the select box value text */
    .stSelectbox [data-baseweb="select"] [data-testid="stSelectbox"],
    .stSelectbox [data-baseweb="select"] [data-testid="stSelectbox"] span,
    .stSelectbox [data-baseweb="select"] input {
        color: #000000 !important;            /* Black text */
    }
    
    /* Number input container and buttons */
    .stNumberInput>div {
        background-color: #000000 !important;  /* Keep number inputs black */
    }
    
    .stNumberInput button {
        background-color: #000000 !important;  /* Keep number inputs black */
        color: #FFFFFF !important;            /* Keep number input text white */
        border: 1px solid #3E3E3E !important;
    }
    
    .stNumberInput button:hover {
        background-color: #1A1A1A !important;
    }
    
    /* Select box dropdown - most specific selectors */
    div[data-baseweb="popover"] div[role="listbox"] div[role="option"],
    div[data-baseweb="popover"] div[role="listbox"] div[role="option"] span,
    div[data-baseweb="popover"] div[role="listbox"] div[role="option"] div,
    div[data-baseweb="popover"] div[role="listbox"] div[role="option"] p,
    div[data-baseweb="popover"] div[role="listbox"] div[role="option"] *,
    div[data-baseweb="popover"] div[role="listbox"] div[role="option"] div[data-testid="stSelectbox"],
    div[data-baseweb="popover"] div[role="listbox"] div[role="option"] div[data-testid="stSelectbox"] span,
    div[data-baseweb="popover"] div[role="listbox"] div[role="option"] div[data-testid="stSelectbox"] div,
    div[data-baseweb="popover"] div[role="listbox"] div[role="option"] div[data-testid="stSelectbox"] p,
    div[data-baseweb="popover"] div[role="listbox"] div[role="option"] div[data-testid="stSelectbox"] * {
        color: #000000 !important;            /* Force black text for all dropdown options */
        background-color: #FFFFFF !important;  /* White background */
    }
    
    /* Ensure the text stays black even when selected or hovered */
    div[data-baseweb="popover"] div[role="listbox"] div[role="option"][aria-selected="true"],
    div[data-baseweb="popover"] div[role="listbox"] div[role="option"]:hover,
    div[data-baseweb="popover"] div[role="listbox"] div[role="option"][aria-selected="true"] *,
    div[data-baseweb="popover"] div[role="listbox"] div[role="option"]:hover *,
    div[data-baseweb="popover"] div[role="listbox"] div[role="option"][aria-selected="true"] div[data-testid="stSelectbox"] *,
    div[data-baseweb="popover"] div[role="listbox"] div[role="option"]:hover div[data-testid="stSelectbox"] * {
        color: #000000 !important;            /* Keep text black even when selected/hovered */
        background-color: #FFFFFF !important;  /* Keep white background */
    }
    
    /* Target the select box container */
    .stSelectbox>div>div[data-baseweb="select"] {
        background-color: #FFFFFF !important;  /* White background */
        color: #000000 !important;            /* Black text */
        border: 1px solid #3E3E3E !important;
    }
    
    /* Target the select box value text */
    .stSelectbox [data-baseweb="select"] [data-testid="stSelectbox"],
    .stSelectbox [data-baseweb="select"] [data-testid="stSelectbox"] span,
    .stSelectbox [data-baseweb="select"] [data-testid="stSelectbox"] div,
    .stSelectbox [data-baseweb="select"] [data-testid="stSelectbox"] p,
    .stSelectbox [data-baseweb="select"] [data-testid="stSelectbox"] * {
        color: #000000 !important;            /* Black text */
        background-color: #FFFFFF !important;  /* White background */
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #262730;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #FFFFFF;
    }
    
    /* Plot styling */
    .js-plotly-plot {
        background-color: #262730 !important;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: #1E3A1E;
        color: #4CAF50;
    }
    
    .stError {
        background-color: #3A1E1E;
        color: #F44336;
    }
    
    /* Metric values */
    .stMetric {
        color: #FFFFFF;
    }
    
    .stMetric label {
        color: #FFFFFF !important;
    }
    
    /* Sidebar text - make it dark */
    .css-1d391kg, 
    .css-1d391kg *,
    .css-1d391kg p,
    .css-1d391kg div,
    .css-1d391kg span,
    .css-1d391kg label,
    .css-1d391kg h1,
    .css-1d391kg h2,
    .css-1d391kg h3,
    .css-1d391kg h4,
    .css-1d391kg h5,
    .css-1d391kg h6 {
        color: #FFFFFF !important;
    }
    
    /* Make sure all text in the app is white */
    .stMarkdown, .stMarkdown * {
        color: #FFFFFF !important;
    }
    
    /* Ensure form field labels are visible */
    .stForm label, .stForm .stMarkdown {
        color: #FFFFFF !important;
    }
    
    /* Make sure all headers are visible */
    h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #FFFFFF !important;
    }
    
    /* Target select boxes in the signup form specifically */
    .stForm .stSelectbox>div>div[data-baseweb="select"],
    .stForm .stSelectbox>div>div[data-baseweb="select"] > div,
    .stForm .stSelectbox>div>div[data-baseweb="select"] input,
    .stForm .stSelectbox>div>div[data-baseweb="select"] span,
    .stForm .stSelectbox>div>div[data-baseweb="select"] * {
        background-color: #FFFFFF !important;  /* White background */
        color: #000000 !important;            /* Black text */
    }
    
    /* Target the dropdown menu specifically */
    .stForm div[data-baseweb="popover"] div[role="listbox"],
    .stForm div[data-baseweb="popover"] div[role="listbox"] div[role="option"],
    .stForm div[data-baseweb="popover"] div[role="listbox"] div[role="option"] span,
    .stForm div[data-baseweb="popover"] div[role="listbox"] div[role="option"] div,
    .stForm div[data-baseweb="popover"] div[role="listbox"] div[role="option"] p,
    .stForm div[data-baseweb="popover"] div[role="listbox"] div[role="option"] * {
        background-color: #FFFFFF !important;  /* White background */
        color: #000000 !important;            /* Black text */
    }
    
    /* Override any other styles that might be affecting the select boxes */
    .stForm .stSelectbox *,
    .stForm div[data-baseweb="popover"] * {
        color: #000000 !important;            /* Force black text */
    }
    
    /* Target all select box elements */
    .stSelectbox *,
    .stSelectbox>div>div[data-baseweb="select"] *,
    .stSelectbox>div>div[data-baseweb="select"] input,
    .stSelectbox>div>div[data-baseweb="select"] span,
    .stSelectbox>div>div[data-baseweb="select"] div {
        color: #000000 !important;            /* Force black text */
    }
    
    /* Target the dropdown menu and all its contents */
    div[data-baseweb="popover"] *,
    div[data-baseweb="popover"] div[role="listbox"] *,
    div[data-baseweb="popover"] div[role="option"] *,
    div[data-baseweb="popover"] div[role="option"] span,
    div[data-baseweb="popover"] div[role="option"] div,
    div[data-baseweb="popover"] div[role="option"] p {
        color: #000000 !important;            /* Force black text */
        background-color: #FFFFFF !important;  /* White background */
    }
    
    /* Ensure selected and hover states maintain black text */
    div[data-baseweb="popover"] div[role="option"][aria-selected="true"] *,
    div[data-baseweb="popover"] div[role="option"]:hover * {
        color: #000000 !important;            /* Keep text black */
    }
    
    /* Target the select box container */
    .stSelectbox>div>div[data-baseweb="select"] {
        background-color: #FFFFFF !important;  /* White background */
        color: #000000 !important;            /* Black text */
        border: 1px solid #3E3E3E !important;
    }
    
    /* Form labels - make select box labels white with more specific selectors */
    .stSelectbox label,
    .stSelectbox label p,
    .stSelectbox label div,
    .stSelectbox label span,
    .stSelectbox [data-testid="stSelectbox"] label,
    .stSelectbox [data-testid="stSelectbox"] label p,
    .stSelectbox [data-testid="stSelectbox"] label div,
    .stSelectbox [data-testid="stSelectbox"] label span,
    .stSelectbox [data-baseweb="select"] label,
    .stSelectbox [data-baseweb="select"] label p,
    .stSelectbox [data-baseweb="select"] label div,
    .stSelectbox [data-baseweb="select"] label span,
    div[data-testid="stSelectbox"] label,
    div[data-testid="stSelectbox"] label p,
    div[data-testid="stSelectbox"] label div,
    div[data-testid="stSelectbox"] label span {
        color: #FFFFFF !important;            /* Force white text for select box labels */
    }
    
    /* Override any other styles that might be affecting the labels */
    .stForm .stSelectbox label *,
    .stForm div[data-testid="stSelectbox"] label * {
        color: #FFFFFF !important;            /* Force white text for all label elements */
    }
    
    /* Sidebar profile information - make it dark */
    .css-1d391kg div[data-testid="stVerticalBlock"] div[data-testid="stMarkdownContainer"] p,
    .css-1d391kg div[data-testid="stVerticalBlock"] div[data-testid="stMarkdownContainer"] *,
    .css-1d391kg div[data-testid="stVerticalBlock"] div[data-testid="element-container"] p,
    .css-1d391kg div[data-testid="stVerticalBlock"] div[data-testid="element-container"] *,
    .css-1d391kg div[data-testid="stVerticalBlock"] div[data-testid="stMarkdownContainer"],
    .css-1d391kg div[data-testid="stVerticalBlock"] div[data-testid="element-container"],
    .css-1d391kg div[data-testid="stVerticalBlock"] div[data-testid="stMarkdownContainer"] div,
    .css-1d391kg div[data-testid="stVerticalBlock"] div[data-testid="element-container"] div,
    .css-1d391kg div[data-testid="stVerticalBlock"] div[data-testid="stMarkdownContainer"] span,
    .css-1d391kg div[data-testid="stVerticalBlock"] div[data-testid="element-container"] span {
        color: #262730 !important;  /* Dark gray text */
    }
    
    /* Override any other styles that might be affecting the profile text */
    .css-1d391kg div[data-testid="stVerticalBlock"] * {
        color: #262730 !important;  /* Dark gray text */
    }
    
    /* Keep the sidebar background light */
    .css-1d391kg {
        background-color: #FFFFFF !important;
    }
    
    /* Force black text for sidebar profile information with highest specificity */
    .css-1d391kg div[data-testid="stVerticalBlock"] div[data-testid="stMarkdownContainer"] div.profile-info,
    .css-1d391kg div[data-testid="stVerticalBlock"] div[data-testid="stMarkdownContainer"] div.profile-info *,
    .css-1d391kg div[data-testid="stVerticalBlock"] div[data-testid="stMarkdownContainer"] div.profile-info p,
    .css-1d391kg div[data-testid="stVerticalBlock"] div[data-testid="stMarkdownContainer"] div.profile-info span,
    .css-1d391kg div[data-testid="stVerticalBlock"] div[data-testid="stMarkdownContainer"] div.profile-info div,
    .css-1d391kg div[data-testid="stVerticalBlock"] div[data-testid="stMarkdownContainer"] div.profile-info strong,
    .css-1d391kg div[data-testid="stVerticalBlock"] div[data-testid="stMarkdownContainer"] div.profile-info em {
        color: #000000 !important;  /* Pure black text */
        font-weight: normal !important;
        font-style: normal !important;
        text-decoration: none !important;
        background: none !important;
        border: none !important;
        box-shadow: none !important;
        opacity: 1 !important;
        filter: none !important;
        transform: none !important;
        transition: none !important;
        animation: none !important;
    }
    
    /* Override any Streamlit styles that might be affecting the profile text */
    .css-1d391kg div[data-testid="stVerticalBlock"] div[data-testid="stMarkdownContainer"] div.profile-info *::before,
    .css-1d391kg div[data-testid="stVerticalBlock"] div[data-testid="stMarkdownContainer"] div.profile-info *::after {
        color: #000000 !important;  /* Pure black text */
    }
    
    /* Ensure the profile info container itself has black text */
    .css-1d391kg div[data-testid="stVerticalBlock"] div[data-testid="stMarkdownContainer"] div.profile-info {
        color: #000000 !important;  /* Pure black text */
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0.5rem 0 !important;
        font-size: 1rem !important;
        line-height: 1.5 !important;
    }

    /* Custom sidebar styling */
    .custom-sidebar {
        background-color: #4A4A4A !important;
        padding: 1rem !important;
        border-radius: 0.5rem !important;
        margin: 1rem !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
    }

    .custom-sidebar * {
        color: #FFFFFF !important;
    }

    .custom-sidebar .profile-header {
        font-size: 1.5rem !important;
        font-weight: bold !important;
        margin-bottom: 1rem !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 2px solid #666666 !important;
    }

    .custom-sidebar .profile-info {
        padding: 0.5rem 0 !important;
        border-bottom: 1px solid #666666 !important;
    }

    .custom-sidebar .profile-info:last-child {
        border-bottom: none !important;
    }

    .custom-sidebar .logout-button {
        margin-top: 1rem !important;
        background-color: #FF0000 !important;
        color: #FFFFFF !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 4px !important;
        width: 100% !important;
    }

    .custom-sidebar .logout-button:hover {
        background-color: #CC0000 !important;
    }

    /* Style the sidebar collapse/expand button */
    .stSidebarCollapseButton {
        background-color: #4A4A4A !important;
        color: #FFFFFF !important;
        border: none !important;
    }

    .stSidebarCollapseButton:hover {
        background-color: #666666 !important;
    }

    /* Style the collapse button icon */
    .stSidebarCollapseButton svg {
        fill: #FFFFFF !important;
    }

    .stSidebarCollapseButton:hover svg {
        fill: #CCCCCC !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Session state initialization
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

def login_page():
    st.title("Welcome to NutriChat 🥗")
    st.markdown("### Your AI Nutrition Coach")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login to NutriChat")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            if not email or not password:
                st.error("Please enter both email and password")
            else:
                try:
                    user = verify_password(email, password)
                    if user:
                        st.success("Welcome back to NutriChat!")
                        st.session_state.user_id = user['user_id']
                        st.session_state.user_data = user
                        st.rerun()
                    else:
                        st.error("Invalid email or password")
                except Exception as e:
                    st.error(f"Error during login: {str(e)}")
    
    with tab2:
        st.subheader("Join NutriChat")
        with st.form("signup_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Age", min_value=13, max_value=120)
                height = st.number_input("Height (inches)", min_value=20, max_value=100)
                weight = st.number_input("Weight (lbs)", min_value=50, max_value=661)
            
            with col2:
                sex = st.selectbox("Sex", ["male", "female", "other"])
                activity_level = st.selectbox("Activity Level", list(ACTIVITY_LEVELS.keys()))
                goal = st.selectbox("Goal", list(GOALS.keys()))
            
            submitted = st.form_submit_button("Create Account")
            if submitted:
                if password != confirm_password:
                    st.error("Passwords do not match!")
                else:
                    # Validate user data
                    validation = validate_user_data(
                        email=email,
                        password=password,
                        age=age,
                        height=height,
                        weight=weight,
                        sex=sex,
                        activity_level=activity_level,
                        goal=goal
                    )
                    
                    if not validation['is_valid']:
                        for field, error in validation['errors'].items():
                            st.error(f"{field.title()}: {error}")
                    else:
                        try:
                            # Create user account
                            user_id = insert_user(
                                email=email,
                                password=password,
                                age=age,
                                height=height,
                                weight=weight,
                                sex=sex,
                                activity_level=activity_level,
                                goal=goal
                            )
                            
                            # Get user data and set session
                            user = get_user(user_id)
                            if user:
                                st.success("Welcome to NutriChat!")
                                st.session_state.user_id = user_id
                                st.session_state.user_data = user
                                st.rerun()
                            else:
                                st.error("Account created but failed to log in. Please try logging in.")
                        except ValueError as e:
                            st.error(str(e))  # Handle email already exists
                        except Exception as e:
                            st.error(f"Error creating account: {str(e)}")

def dashboard_page():
    st.title("NutriChat Dashboard 📊")
    
    # Initialize AI coach
    ai_coach = NutritionCoach()
    
    # User info sidebar with custom styling
    with st.sidebar:
        sidebar_content = f"""
        <div class="custom-sidebar">
            <div class="profile-header">Your Profile</div>
            <div class="profile-info">Email: {st.session_state.user_data['email']}</div>
            <div class="profile-info">Age: {st.session_state.user_data['age']}</div>
            <div class="profile-info">Sex: {st.session_state.user_data['sex']}</div>
            <div class="profile-info">Height: {st.session_state.user_data['height']} inches</div>
            <div class="profile-info">Weight: {st.session_state.user_data['weight']} lbs</div>
            <div class="profile-info">Activity Level: {st.session_state.user_data['activity_level']}</div>
            <div class="profile-info">Goal: {st.session_state.user_data['goal']}</div>
        </div>
        """
        st.markdown(sidebar_content, unsafe_allow_html=True)
        
        if st.button("Logout", key="logout_button"):
            st.session_state.user_id = None
            st.session_state.user_data = None
            st.rerun()
    
    # Main dashboard content
    # Add AI Coach section
    st.subheader("AI Nutrition Coach 🤖")
    
    # Create tabs for different AI features
    ai_tab1, ai_tab2 = st.tabs(["Personalized Advice", "Progress Analysis"])
    
    with ai_tab1:
        st.markdown("### Your Personalized Nutrition Plan")
        if st.button("Get AI Advice", key="get_advice"):
            try:
                # Get user's nutrition profile
                profile = calculate_nutrition_profile(
                    weight_lbs=st.session_state.user_data['weight'],
                    height_inches=st.session_state.user_data['height'],
                    age=st.session_state.user_data['age'],
                    sex=st.session_state.user_data['sex'],
                    activity_level=st.session_state.user_data['activity_level'],
                    goal=st.session_state.user_data['goal']
                )
                
                # Get AI advice
                advice = ai_coach.get_personalized_advice(
                    profile=profile,
                    goal=st.session_state.user_data['goal']
                )
                
                # Display advice in a clean format
                st.markdown("#### Meal Plan")
                st.markdown(advice['meal_plan'])
                
                st.markdown("#### Nutrition Tips")
                st.markdown(advice['nutrition_tips'])
                
                st.markdown("#### Lifestyle Tips")
                st.markdown(advice['lifestyle_tips'])
                
            except Exception as e:
                st.error(f"Error getting AI advice: {str(e)}")
    
    with ai_tab2:
        st.markdown("### Progress Analysis")
        if st.button("Analyze Progress", key="analyze_progress"):
            try:
                # Get user's nutrition profile
                profile = calculate_nutrition_profile(
                    weight_lbs=st.session_state.user_data['weight'],
                    height_inches=st.session_state.user_data['height'],
                    age=st.session_state.user_data['age'],
                    sex=st.session_state.user_data['sex'],
                    activity_level=st.session_state.user_data['activity_level'],
                    goal=st.session_state.user_data['goal']
                )
                
                # Get logs for analysis
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                logs = get_logs(st.session_state.user_id, start_date, end_date)
                
                if not logs:
                    st.info("No logs available for analysis. Start logging your meals to get personalized feedback.")
                else:
                    # Get AI analysis
                    analysis = ai_coach.analyze_progress(
                        profile=profile,
                        logs=logs,
                        goal=st.session_state.user_data['goal']
                    )
                    
                    # Display analysis in a clean format
                    st.markdown("#### Progress Summary")
                    st.markdown(analysis['summary'])
                    
                    st.markdown("#### Recommendations")
                    st.markdown(analysis['recommendations'])
                
            except Exception as e:
                st.error(f"Error analyzing progress: {str(e)}")
    
    # Add a divider before the existing nutrition logging section
    st.markdown("---")
    
    # Existing nutrition logging section
    st.subheader("Log Today's Nutrition")
    with st.form("nutrition_log"):
        col1, col2 = st.columns(2)
        with col1:
            # Use user's initial weight from profile as default
            initial_weight = st.session_state.user_data['weight']
            weight = st.number_input("Weight (lbs)", min_value=50.0, max_value=661.0, value=float(initial_weight), step=0.5)
            calories = st.number_input("Calories", min_value=0, max_value=10000, value=2000, step=1)
        with col2:
            protein = st.number_input("Protein (g)", min_value=0, max_value=500, value=150, step=1)
            carbs = st.number_input("Carbs (g)", min_value=0, max_value=1000, value=200, step=1)
            fat = st.number_input("Fat (g)", min_value=0, max_value=500, value=70, step=1)
        
        if st.form_submit_button("Save Log"):
            try:
                # Validate log data
                validation = validate_log_data(
                    user_id=st.session_state.user_id,
                    weight=weight,
                    calories=calories,
                    protein=protein,
                    carbs=carbs,
                    fat=fat
                )
                
                if not validation['is_valid']:
                    for field, error in validation['errors'].items():
                        st.error(f"{field.title()}: {error}")
                else:
                    # Save the log
                    log_id = insert_log(
                        user_id=st.session_state.user_id,
                        weight=weight,
                        calories=calories,
                        protein=protein,
                        carbs=carbs,
                        fat=fat
                    )
                    st.success("Log saved successfully!")
                    st.rerun()  # Refresh to show updated data
            except Exception as e:
                st.error(f"Error saving log: {str(e)}")
    
    # Get user's logs for the last 30 days
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    user_logs = get_logs(st.session_state.user_id, start_date, end_date)
    
    # Convert logs to DataFrame for easier plotting
    if user_logs:
        df_logs = pd.DataFrame(user_logs)
        df_logs['date'] = pd.to_datetime(df_logs['date'])
        df_logs = df_logs.sort_values('date')
        
        # Calculate metrics
        latest_log = df_logs.iloc[-1].to_dict()  # Convert to dictionary
        previous_log = df_logs.iloc[-2].to_dict() if len(df_logs) > 1 else None
        
        # Update metrics with real data
        if previous_log:
            weight_change = f"{latest_log['weight'] - previous_log['weight']:.1f} lbs"
            calorie_change = f"{latest_log['calories'] - previous_log['calories']:.0f}"
        else:
            weight_change = "0 lbs"
            calorie_change = "0"
            
        protein_percent = f"{(latest_log['protein'] / 150) * 100:.0f}%"  # Assuming 150g protein goal
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Weight", f"{latest_log['weight']:.1f} lbs", delta=None)
        with col2:
            st.metric("Daily Calories", f"{latest_log['calories']:.0f}", delta=None)
        with col3:
            st.metric("Protein Goal", f"{latest_log['protein']:.0f}g", delta=None)
        
        # Progress charts
        st.subheader("Progress Charts")
        tab1, tab2, tab3 = st.tabs(["Weight", "Calories", "Macronutrients"])
        
        with tab1:
            fig = px.line(df_logs, x='date', y='weight', 
                         title='Weight Progress',
                         labels={'weight': 'Weight (lbs)', 'date': 'Date'},
                         template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            fig = px.line(df_logs, x='date', y='calories',
                         title='Daily Calorie Intake',
                         labels={'calories': 'Calories (kcal)', 'date': 'Date'},
                         template='plotly_dark')
            fig.update_traces(line=dict(color='#FF0000', width=3))  # Red line for calories
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            fig = px.line(df_logs, x='date', y=['protein', 'carbs', 'fat'],
                         title='Daily Macronutrient Intake',
                         labels={'value': 'Amount (g)', 'variable': 'Macronutrient', 'date': 'Date'},
                         template='plotly_dark',
                         color_discrete_map={
                             'protein': '#FF0000',  # Red for protein
                             'carbs': '#00FF00',    # Green for carbs
                             'fat': '#0000FF'       # Blue for fat
                         })
            fig.update_traces(line=dict(width=3))  # Make lines thicker
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No logs found. Start logging your nutrition to see your progress!")
        # Show default metrics with user's initial weight
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Weight", f"{initial_weight} lbs", delta=None)
        with col2:
            st.metric("Daily Calories", "0", delta=None)
        with col3:
            st.metric("Protein Goal", "0g", delta=None)

def main():
    """Main application entry point."""
    # Initialize database if needed
    try:
        from db import init_db
        init_db()
    except Exception as e:
        st.error(f"Failed to initialize database: {str(e)}")
        return

    # Initialize session state
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None

    # Show login page if not logged in
    if st.session_state.user_id is None:
        login_page()
    else:
        # User is logged in, show dashboard
        dashboard_page()

if __name__ == "__main__":
    main()
