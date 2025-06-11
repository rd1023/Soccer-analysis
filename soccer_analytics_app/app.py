import os
# Set environment variable to allow large uploads (up to 2GB)
os.environ['STREAMLIT_SERVER_MAX_UPLOAD_SIZE'] = '2048'
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import subprocess
from pathlib import Path

# ----------------------------
# Page & Server Configuration
# ----------------------------
st.set_page_config(
    page_title="Soccer Analytics Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# Allow large uploads (up to 2GB)
os.environ['STREAMLIT_SERVER_MAX_UPLOAD_SIZE'] = '2048'

# Custom CSS for clean look
st.markdown(
    '''
    <style>
      body {background-color: #F0F2F6;}
      #MainMenu, footer, header {visibility: hidden;}
      .appview-container {padding: 1rem;}
    </style>
    ''', unsafe_allow_html=True
)

# ----------------------------
# Landing Section
# ----------------------------
if 'video_uploaded' not in st.session_state:
    st.image("https://via.placeholder.com/600x120?text=Soccer+Analytics+Pro", use_column_width=True)
    st.title("Welcome to Soccer Analytics Pro")
    st.write(
        "Upload a full match recording (up to 2GB) to analyze events, timelines, and visualize your team's performance."
    )
    if st.button("Get Started"):
        st.session_state['video_uploaded'] = False
    st.stop()

# ----------------------------
# Sidebar: Controls & Video Upload
# ----------------------------
st.sidebar.header("Upload & Filters")
# Video uploader
uploaded_video = st.sidebar.file_uploader(
    "Choose full match video (≤2GB)",
    type=["mp4","mov","mkv"],
    accept_multiple_files=False
)
if uploaded_video:
    temp = Path("/tmp")
    temp.mkdir(exist_ok=True)
    video_path = temp / uploaded_video.name
    with open(video_path, 'wb') as f:
        for chunk in uploaded_video.chunks(1024*1024): f.write(chunk)
    st.sidebar.success(f"Saved: {uploaded_video.name}")
    st.session_state['video_uploaded'] = True
    # Trigger analysis
    with st.spinner("Analyzing full match—please wait..."):
        subprocess.run(["python","main.py","--video_path",str(video_path)])

# Time and event filters
if 'video_uploaded' in st.session_state:
    st.sidebar.subheader("Filters")
    df = pd.read_json('output/match_events.json') if Path('output/match_events.json').exists() else pd.DataFrame()
    if not df.empty:
        max_min = int(df['timestamp'].max()//60)
        time_range = st.sidebar.slider("Minute range", 0, max_min, (0, max_min))
        types = df['type'].unique().tolist()
        selected = st.sidebar.multiselect("Event types", types, default=types)
    else:
        time_range, selected = (0,0), []
else:
    st.write("No video uploaded yet.")
    st.stop()

# ----------------------------
# Header Display
# ----------------------------
col1, col2, col3 = st.columns([1,6,1])
with col1: st.image("https://via.placeholder.com/80?text=Home", width=80)
with col2:
    st.markdown("### Home FC vs Away United")
    st.markdown("#### Match Date: 2025-06-10")
with col3: st.image("https://via.placeholder.com/80?text=Away", width=80)
st.markdown("---")

# ----------------------------
# Main Tabs
# ----------------------------
t1,t2,t3,t4 = st.tabs(["📊 Summary","📋 Events","⏱ Timeline","⚽ Pitch Map"])

# Load and filter data
df = pd.read_json('output/match_events.json') if Path('output/match_events.json').exists() else pd.DataFrame()
if not df.empty:
    df = df[(df['timestamp']/60>=time_range[0])&(df['timestamp']/60<=time_range[1])]
    df = df[df['type'].isin(selected)]

with t1:
    st.subheader("Match Overview")
    if df.empty:
        st.info("No events detected.")
    else:
        shots = int((df['type']=='shot').sum())
        xg = round(df['xG'].sum(),2) if 'xG' in df else 0.0
        poss = int((df['type']=='possession').sum())
        cols = st.columns(3)
        cols[0].metric("Total Shots", shots)
        cols[1].metric("Total xG", xg)
        cols[2].metric("Possession Changes", poss)

with t2:
    st.subheader("Events Table")
    st.dataframe(df.reset_index(drop=True), use_container_width=True)

with t3:
    st.subheader("Event Timeline")
    if not df.empty:
        df['min']=(df['timestamp']//60).astype(int)
        tl=df.groupby(['min','type']).size().reset_index(name='count')
        fig=px.bar(tl, x='min', y='count', color='type', barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No timeline data.")

with t4:
    st.subheader("Pitch Map")
    if not df.empty and 'x_m' in df:
        fig=go.Figure(); fig.update_layout(xaxis=dict(range=[0,105],visible=False), yaxis=dict(range=[0,68],visible=False), height=400)
        fig.add_trace(go.Scatter(x=df['x_m'],y=df['y_m'],mode='markers',marker=dict(size=8,color='blue')))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No positional data.")
