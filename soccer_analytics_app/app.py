# Main Streamlit App with full AI features
import streamlit as st
import pandas as pd
from utils.tagging import create_event, save_events
from utils.overlay import plot_event_on_field
from utils.player_report import generate_player_report
from utils.ai_tagging import detect_xg_moments
from utils.pdf_export import generate_pdf_report
from utils.xg_model import calculate_xg
from utils.heatmap import plot_heatmap
from utils.scouting_report import generate_scouting_report
from utils.yolo_tagging import detect_with_yolo
from utils.whisper_tagging import detect_voice_tags
from utils.match_summary import generate_summary
import time

st.set_page_config(layout="wide")
st.title("Lulu Analysis - Soccer Match Intelligence")

st.sidebar.header("Upload Match Video")
video = st.sidebar.file_uploader("Choose a .mp4 file", type=["mp4"])
audio = st.sidebar.file_uploader("Optional: Upload audio for voice tagging (.wav)", type=["wav"])

event_log = []

if video:
    st.video(video)

    st.sidebar.header("Tag Event")
    timestamp = st.sidebar.number_input("Timestamp (seconds)", step=1)
    event_type = st.sidebar.selectbox("Event Type", ["Pass", "Shot", "Goal", "Tackle", "Interception", "Dribble", "Clearance"])
    player = st.sidebar.text_input("Player Name/#")
    location = st.sidebar.text_input("Location (e.g. 200,150 for X,Y)")
    notes = st.sidebar.text_area("Additional Notes")

    if st.sidebar.button("Tag Event"):
        event = create_event(event_type, timestamp, player, location, notes)
        if event_type == "Shot":
            event["xG"] = calculate_xg(event)
        event_log.append(event)
        st.success(f"Event tagged: {event_type} at {timestamp}s")

    if st.sidebar.button("Run AI Detection"):
        st.info("Running AI xG tagging (mock)...")
        ai_events = detect_xg_moments(video.name)
        for event in ai_events:
            if event["Event Type"] == "Shot":
                event["xG"] = calculate_xg(event)
        event_log.extend(ai_events)
        st.success(f"{len(ai_events)} xG moments detected.")

    if st.sidebar.button("YOLO Auto Tagging"):
        yolo_events = detect_with_yolo(video.name)
        for event in yolo_events:
            if event["Event Type"] == "Shot":
                event["xG"] = calculate_xg(event)
        event_log.extend(yolo_events)
        st.success(f"{len(yolo_events)} events auto-tagged by YOLO.")

    if audio and st.sidebar.button("Whisper Voice Tagging"):
        voice_tags = detect_voice_tags(audio.name)
        for event in voice_tags:
            if event["Event Type"] == "Shot":
                event["xG"] = calculate_xg(event)
        event_log.extend(voice_tags)
        st.success(f"{len(voice_tags)} events tagged via voice commands.")

    if st.sidebar.button("Save Events"):
        save_events(event_log)
        st.success("Events saved to CSV")

    st.header("Tagged Events Log")
    if event_log:
        df_log = pd.DataFrame(event_log)
        st.dataframe(df_log)

        if st.button("Generate Match PDF Report"):
            generate_pdf_report(event_log)
            st.success("Match report saved to output/reports/match_report.pdf")

        if st.button("Generate Scouting Report"):
            generate_scouting_report(event_log)
            st.success("Scouting report saved to output/reports/scouting_report.pdf")

        if st.button("Generate AI Match Summary"):
            summary = generate_summary(event_log)
            st.text_area("AI Match Summary", value=summary, height=150)

    st.header("Player Report + Heatmap")
    uploaded_file = st.file_uploader("Upload tagged events CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        player_query = st.text_input("Enter player name/#")
        if player_query:
            report = generate_player_report(df, player_query)
            st.subheader("Event Count")
            st.dataframe(report)
            heatmap = plot_heatmap(df, player_query)
            if heatmap:
                st.pyplot(heatmap)
            else:
                st.warning("No location data available for heatmap.")

    st.header("Tactical Overlay")
    if st.button("Sample Event on Field"):
        fig = plot_event_on_field((200, 120))
        st.pyplot(fig)
