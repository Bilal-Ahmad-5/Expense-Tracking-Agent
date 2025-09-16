import streamlit as st

def apply_custom_styles():
    """Apply custom CSS styles to enhance the app's appearance"""
    
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles - Beautiful Background */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: radial-gradient(circle at 10% 20%, rgba(255, 255, 255, 0.9) 0%, rgba(240, 245, 255, 0.9) 100%);
        min-height: 100vh;
        background-image: 
            radial-gradient(circle at 85% 30%, rgba(214, 230, 255, 0.3) 0%, transparent 25%),
            radial-gradient(circle at 15% 70%, rgba(224, 240, 255, 0.4) 0%, transparent 25%);
        background-attachment: fixed;
    }
    
    /* Main Container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: rgba(255, 255, 255, 0.85);
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(100, 149, 237, 0.15);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        margin: 1rem;
    }
    
    /* Header Styles */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #8aaae5 0%, #b8c7ff 100%);
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(138, 170, 229, 0.25);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 300;
    }
    
    /* Sidebar Styles */
    .css-1d391kg {
        background: rgba(245, 248, 255, 0.7);
        border-right: 1px solid rgba(200, 215, 255, 0.4);
        backdrop-filter: blur(8px);
    }
    
    /* Metric Cards */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.7);
        border: 1px solid rgba(200, 215, 255, 0.6);
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(138, 170, 229, 0.1);
        transition: transform 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(138, 170, 229, 0.2);
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #8aaae5 0%, #b8c7ff 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(138, 170, 229, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(138, 170, 229, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0px);
    }
    
    /* File Uploader */
    div[data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.7);
        border: 2px dashed #8aaae5;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    div[data-testid="stFileUploader"]:hover {
        border-color: #b8c7ff;
        background: rgba(255, 255, 255, 0.9);
    }
    
    /* Input Fields */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        border-radius: 12px;
        border: 1px solid rgba(138, 170, 229, 0.3);
        padding: 0.75rem;
        transition: all 0.3s ease;
        background: rgba(255, 255, 255, 0.8);
    }
    
    .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox select:focus {
        border-color: #8aaae5;
        box-shadow: 0 0 0 3px rgba(138, 170, 229, 0.1);
        background: white;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.7);
        border-radius: 15px;
        padding: 0.5rem;
        border: 1px solid rgba(138, 170, 229, 0.2);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #8aaae5 0%, #b8c7ff 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(138, 170, 229, 0.25);
    }
    
    /* Success Messages */
    .stSuccess {
        background: linear-gradient(135deg, #a8e6cf 0%, #dcedc1 100%);
        border-radius: 10px;
        padding: 1rem;
        border: none;
        color: #1a3b2d;
        font-weight: 500;
    }
    
    /* Error Messages */
    .stError {
        background: linear-gradient(135deg, #ffaaa5 0%, #ffd3b6 100%);
        border-radius: 10px;
        padding: 1rem;
        border: none;
        color: #7a0c2e;
        font-weight: 500;
    }
    
    /* Info Messages */
    .stInfo {
        background: linear-gradient(135deg, #a7d7c5 0%, #c1e3ff 100%);
        border-radius: 10px;
        padding: 1rem;
        border: none;
        color: #1a3b2d;
        font-weight: 500;
    }
    
    /* Warning Messages */
    .stWarning {
        background: linear-gradient(135deg, #ffd3b6 0%, #ffaaa5 100%);
        border-radius: 10px;
        padding: 1rem;
        border: none;
        color: #7a4a0c;
        font-weight: 500;
    }
    
    /* Container styling */
    .element-container {
        margin-bottom: 1rem;
    }
    
    /* Chart containers */
    .js-plotly-plot {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(138, 170, 229, 0.1);
        background: rgba(255, 255, 255, 0.7);
    }
    
    /* Loading spinner */
    .stSpinner {
        border-top-color: #8aaae5 !important;
    }
    
    /* Custom expense card */
    .expense-card {
        background: rgba(255, 255, 255, 0.7);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(138, 170, 229, 0.3);
        box-shadow: 0 4px 12px rgba(138, 170, 229, 0.1);
        transition: transform 0.3s ease;
    }
    
    .expense-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(138, 170, 229, 0.15);
    }
    
    /* Data table styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid rgba(138, 170, 229, 0.2);
    }
    
    .dataframe thead th {
        background: linear-gradient(135deg, #8aaae5 0%, #b8c7ff 100%);
        color: white;
        font-weight: 600;
        border: none;
    }
    
    .dataframe tbody tr:hover {
        background-color: rgba(138, 170, 229, 0.05);
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .element-container {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main .block-container {
            margin: 0.5rem;
            padding: 1rem;
        }
        
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main-header {
            padding: 1.5rem 1rem;
        }
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5ff;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #8aaae5;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #6b8cce;
    }
    </style>
    """, unsafe_allow_html=True)