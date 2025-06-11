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
    page_title='Soccer Analytics Pro',
    page_icon='⚽',
    layout='wide',
    initial_sidebar_state='expanded'
)
# Allow large uploads (up to 2GB)
st.set_option('server.maxUploadSize', 2048)
# Hide Streamlit branding UI elements
st.markdown(
    '''
    <style>
      #MainMenu {visibility: hidden;}
      header {visibility: hidden;}
      footer {visibility: hidden;}
    </style>
    ''', unsafe_allow_html=True
)

# ----------------------------
# Authentication (Stub)
# ----------------------------
from streamlit_authenticator import Authenticate
credentials = {'usernames': {'admin': {'name': 'Admin', 'password': 'abc123'}}}
auth = Authenticate(credentials, 'cookie', 'signature_key', cookie_expiry_days=1)
user, auth_status = auth.login('Login', 'sidebar')
if not auth_status:
    st.stop()

# ----------------------------
# Sidebar: Controls & Upload
# ----------------------------
st.sidebar.title('Controls')
from streamlit_lottie import st_lottie
import urllib.request
lottie_url = 'https://assets1.lottiefiles.com/packages/lf20_jcikwtux.json'
st_lottie(json.loads(urllib.request.urlopen(lottie_url).read()), height=150)

# Video uploader
uploaded_video = st.sidebar.file_uploader(
    'Upload full match video (≤2GB)', type=['mp4','mov','mkv']
)
# Filters
time_min, time_max = st.sidebar.slider('Minute range', 0, 95, (0, 95))
event_types = ['shot','cross','duel','pass','corner','foul','offside']
selected_types = st.sidebar.multiselect('Event types', event_types, default=event_types)
# AI insights toggle
show_ai = st.sidebar.checkbox('Enable AI Insights')

# ----------------------------
# Handle Video & Analysis
# ----------------------------
video_path = None
if uploaded_video:
    tmp = Path('/tmp')
    tmp.mkdir(exist_ok=True)
    video_path = tmp / uploaded_video.name
    with open(video_path, 'wb') as f:
        for chunk in uploaded_video.chunks(1024*1024):
            f.write(chunk)
    st.sidebar.success(f'Saved {uploaded_video.name}')
    # Run analysis once per session
    if 'analyzed' not in st.session_state:
        with st.spinner('Analyzing full match, please wait...'):
            subprocess.run(['python','main.py','--video_path',str(video_path)], check=True)
            st.session_state['analyzed'] = True

# ----------------------------
# Load & Filter Events
# ----------------------------
events = []
data_file = Path('output/match_events.json')
if data_file.exists():
    events = json.loads(data_file.read_text())
else:
    sample = Path('sample_data/sample_events.json')
    if sample.exists(): events = json.loads(sample.read_text())

df = pd.json_normalize(events) if events else pd.DataFrame()
if not df.empty:
    df = df[(df['timestamp']/60 >= time_min) & (df['timestamp']/60 <= time_max)]
    df = df[df['type'].isin(selected_types)]

# ----------------------------
# Header: Teams & Date
# ----------------------------
home, away = 'Home FC','Away United'
date = '2025-06-10'
col1, col2, col3 = st.columns([1,6,1])
with col1: st.image('assets/home_logo.png', width=80)
with col2:
    st.markdown(f'# {home} vs {away}')
    st.markdown(f'**Date:** {date}')
with col3: st.image('assets/away_logo.png', width=80)
st.markdown('---')

# ----------------------------
# Compute Overview Stats
# ----------------------------
def compute_stats(df):
    if df.empty: return {}
    return {
        'Shots': int((df['type']=='shot').sum()),
        'Corners': int((df['type']=='corner').sum()),
        'Fouls': int((df['type']=='foul').sum()),
        'Offsides': int((df['type']=='offside').sum()),
        'xG': round(df.get('xG', pd.Series()).sum(),2)
    }
stats = compute_stats(df)

# ----------------------------
# Main Tabs
# ----------------------------
t1,t2,t3,t4,t5 = st.tabs([
    '📊 Overview','📋 Events','⏱ Timeline','⚽ Pitch','🔍 AI'
])

with t1:
    st.subheader('Match Overview')
    if not stats: st.info('No data available.')
    else:
        cols = st.columns(len(stats))
        for i,(k,v) in enumerate(stats.items()): cols[i].metric(k, v)

with t2:
    st.subheader('Events Table')
    st.dataframe(df, use_container_width=True)

with t3:
    st.subheader('Event Timeline')
    if not df.empty:
        df['min'] = (df['timestamp']//60).astype(int)
        tl = df.groupby(['min','type']).size().reset_index(name='count')
        fig=px.bar(tl,x='min',y='count',color='type',barmode='group')
        st.plotly_chart(fig, use_container_width=True)

with t4:
    st.subheader('Pitch Map')
    if not df.empty and 'x_m' in df:
        fig=go.Figure();fig.update_layout(xaxis=dict(range=[0,105],visible=False),yaxis=dict(range=[0,68],visible=False),height=400)
        fig.add_trace(go.Scatter(x=df['x_m'],y=df['y_m'],mode='markers',marker=dict(size=8,color='blue')))
        st.plotly_chart(fig, use_container_width=True)
    else: st.info('No positional data.')

with t5:
    st.subheader('AI Insights')
    if show_ai and not df.empty:
        q=st.text_input('Ask AI about data:')
        if st.button('Submit'):
            openai.api_key=st.secrets['OPENAI_API_KEY']
            prompt=f"Data cols: {df.columns.tolist()}. Question: {q}."
            res=openai.ChatCompletion.create(model='gpt-4',messages=[{'role':'user','content':prompt}])
            st.write(res.choices[0].message.content)
    else:
        st.write('Enable AI Insights via sidebar.')
