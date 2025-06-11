import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import subprocess
from pathlib import Path
# 1) Use your theme from config.toml – no need for inline CSS here

# 2) Set up a bold, two‐column hero header
col1, col2 = st.columns([2,3], gap="large")
with col1:
    st.image("https://via.placeholder.com/1200x200?text=Lulu+Soccer+Match+Intelligence",
             use_column_width=True)
with col2:
    st.markdown("## Soccer Match Intelligence")
    st.markdown(
        "Analyze full 135′ matches with event marking, timelines, heatmaps, "
        "and AI insights—all in one place."
    )
    if st.button("🚀 Upload & Analyze", use_container_width=True):
        st.session_state.started = True
st.markdown("---")

)
st.markdown(
    """
    <style>
      #MainMenu, header, footer {visibility: hidden;}
      body {background-color: #F0F2F6;}
      .appview-container {padding: 1rem;}
      .stButton>button {width: 100%; padding: 1rem; font-size: 1.1rem;}
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# Landing Screen / Hero Section
# ----------------------------
if 'started' not in st.session_state:
    st.markdown(
        """
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin-top: 50px;
            margin-bottom: 50px;
        ">
            <img src="https://via.placeholder.com/1000x200?text=Soccer+Analytics+Pro"
                 style="max-width:80%; height:auto; border-radius:10px; box-shadow:0 4px 12px rgba(0,0,0,0.1);" />
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <h1 style="text-align:center; color:#333333; margin-bottom:10px;">
            Welcome to Soccer Analytics Pro
        </h1>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <p style="
            text-align:center;
            font-size:1.1em;
            color:#555555;
            max-width:600px;
            margin:auto;
        ">
            Upload a full match recording (no size limit) to analyze every event,
            explore timelines, and visualize your team's performance across 135 minutes.
        </p>
        """,
        unsafe_allow_html=True
    )
    if st.button("🚀 Get Started"):
        st.session_state.started = True
    st.stop()

# ----------------------------
# Sidebar: Upload & Filters
# ----------------------------
st.sidebar.header("Upload & Filters")
uploaded = st.sidebar.file_uploader(
    "Upload full match recording (no size limit)",
    type=["mp4", "mov", "mkv"],
    accept_multiple_files=False,
    help="Drag and drop or browse for your full match video"
)
if uploaded:
    tmp = Path('/tmp')
    tmp.mkdir(exist_ok=True)
    vpath = tmp / uploaded.name
    with open(vpath, 'wb') as f:
        for chunk in uploaded.chunks(1024 * 1024):
            f.write(chunk)
    st.sidebar.success(f"Saved: {uploaded.name}")
    # Run your analysis pipeline
    with st.spinner("Analyzing full match—please wait..."):
        subprocess.run(["python", "main.py", "--video_path", str(vpath)], check=True)
    st.sidebar.success("Analysis complete.")

# Load or fallback to sample data
events = []
out = Path('output/match_events.json')
if out.exists():
    events = json.loads(out.read_text())
else:
    sample = Path('sample_data/sample_events.json')
    if sample.exists():
        events = json.loads(sample.read_text())
df = pd.json_normalize(events) if events else pd.DataFrame()

# Sidebar filters
time_min, time_max = 0, 135
selected_types = []
if not df.empty:
    time_min, time_max = st.sidebar.slider("Minute range", 0, 135, (0, 135))
    types = df['type'].unique().tolist()
    selected_types = st.sidebar.multiselect("Event types", types, default=types)

# Apply filters
if not df.empty and selected_types:
    df = df[(df['timestamp'] / 60 >= time_min) & (df['timestamp'] / 60 <= time_max)]
    df = df[df['type'].isin(selected_types)]

# ----------------------------
# Header: Teams & Date
# ----------------------------
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    st.image('https://via.placeholder.com/80?text=Home', width=80)
with col2:
    st.markdown("### Home FC vs Away United")
    st.markdown("**Date:** 2025-06-10")
with col3:
    st.image('https://via.placeholder.com/80?text=Away', width=80)
st.markdown("---")

# ----------------------------
# Main Content Tabs
# ----------------------------
t1, t2, t3, t4 = st.tabs(["📊 Overview", "📋 Events", "⏱ Timeline", "⚽ Pitch Map"])

with t1:
    st.subheader("Match Overview")
    if df.empty:
        st.info("No data to display.")
    else:
        shots = int((df['type'] == 'shot').sum())
        xg = round(df.get('xG', pd.Series()).sum(), 2)
        corners = int((df['type'] == 'corner').sum())
        cols = st.columns(3)
        cols[0].metric("Shots", shots)
        cols[1].metric("Total xG", xg)
        cols[2].metric("Corners", corners)

with t2:
    st.subheader("Events Table")
    st.dataframe(df.reset_index(drop=True), use_container_width=True)

with t3:
    st.subheader("Event Timeline")
    if not df.empty:
        df['min'] = (df['timestamp'] // 60).astype(int)
        tl = df.groupby(['min', 'type']).size().reset_index(name='count')
        fig = px.bar(tl, x='min', y='count', color='type', barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No timeline data.")

with t4:
    st.subheader("Pitch Map")
    if not df.empty and 'x_m' in df.columns:
        fig = go.Figure()
        fig.update_layout(
            xaxis=dict(range=[0, 105], visible=False),
            yaxis=dict(range=[0, 68], visible=False),
            height=400,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        fig.add_trace(go.Scatter(x=df['x_m'], y=df['y_m'], mode='markers',
                                 marker=dict(size=10, color='red')))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No positional data.")

