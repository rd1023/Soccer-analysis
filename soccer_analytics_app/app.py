import streamlit as st
import pandas as pd
import plotly.express as px
from mplsoccer import Pitch
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import io
import numpy as np
from datetime import datetime

# App title
st.title("Coach's Soccer Analysis App: PDF Export")

# Mobile optimization CSS
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        font-size: 16px;
        padding: 10px;
    }
    .stTextInput > input, .stSelectbox > select {
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'match_data' not in st.session_state:
    st.session_state.match_data = {}

# Generate heatmap
def generate_heatmap(positions):
    pitch = Pitch(pitch_color='grass', line_color='white')
    fig, ax = pitch.draw()
    if positions:
        x, y = [], []
        for pos in positions.split(";"):
            try:
                _, xy = pos.split(":")
                x_val, y_val = map(float, xy.split(","))
                x.append(x_val)
                y.append(y_val)
            except:
                pass
        if x:
            sns.kdeplot(x=x, y=y, fill=True, cmap='viridis', alpha=0.5, ax=ax)
    return fig

# Generate PDF report
def generate_pdf_report(match_data):
    pdf_path = "match_report.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Match Report", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Timestamp: {match_data['Timestamp']}", styles['Normal']))
    elements.append(Paragraph(f"Date: {match_data['Date']}", styles['Normal']))
    elements.append(Paragraph(f"Opponent: {match_data['Opponent']}", styles['Normal']))
    elements.append(Paragraph(f"Score: {match_data['Our Score']} - {match_data['Opponent Score']}", styles['Normal']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Match Summary", styles['Heading2']))
    elements.append(Paragraph(f"Key Moments: {match_data['Notes']}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Calculate success rates
    tackle_success = (match_data['Tackles Successful'] / match_data['Tackles Attempted'] * 100) if match_data['Tackles Attempted'] > 0 else 0
    dribble_success = (match_data['Dribbles Successful'] / match_data['Dribbles Attempted'] * 100) if match_data['Dribbles Attempted'] > 0 else 0
    cross_success = (match_data['Crosses Successful'] / match_data['Crosses Attempted'] * 100) if match_data['Crosses Attempted'] > 0 else 0

    elements.append(Paragraph("Team Performance", styles['Heading2']))
    team_data = [
        ["Metric", "Our Team", "Opponent"],
        ["Possession (%)", f"{match_data['Possession (%)']}", f"{100 - match_data['Possession (%)']}"],
        ["Shots (On Target/Total)", f"{match_data['Shots on Target']}/{match_data['Shots']}", "-"],
        ["Passes (Completed/Attempted)", f"{match_data['Passes Completed']}/{match_data['Passes Attempted']}", "-"],
        ["Pass Completion (%)", f"{match_data['Pass Completion (%)']:.1f}", "-"],
        ["Tackles (Successful/Attempted)", f"{match_data['Tackles Successful']}/{match_data['Tackles Attempted']}", "-"],
        ["Tackle Success (%)", f"{tackle_success:.1f}", "-"],
        ["Dribbles (Successful/Attempted)", f"{match_data['Dribbles Successful']}/{match_data['Dribbles Attempted']}", "-"],
        ["Dribble Success (%)", f"{dribble_success:.1f}", "-"],
        ["Crosses (Successful/Attempted)", f"{match_data['Crosses Successful']}/{match_data['Crosses Attempted']}", "-"],
        ["Cross Success (%)", f"{cross_success:.1f}", "-"],
        ["Expected Goals (xG)", f"{match_data['Expected Goals (xG)']:.1f}", f"{match_data['Opponent Expected Goals (xG)']:.1f}"],
        ["Field Tilt (%)", f"{match_data['Field Tilt (%)']}", f"{100 - match_data['Field Tilt (%)']}"],
        ["PPDA", f"{match_data['PPDA']}", "-"],
        ["Set Pieces", f"{match_data['Set Piece Outcomes']}", "-"]
    ]
    table = Table(team_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Player Performance", styles['Heading2']))
    player_data = [
        ["Metric", "Value"],
        ["Goals", match_data['Player Goals']],
        ["Assists", match_data['Player Assists']],
        ["Shot-Creating Actions (SCA)", match_data['Shot-Creating Actions (SCA)']],
        ["Goal-Creating Actions (GCA)", match_data['Goal-Creating Actions (GCA)']],
        ["Expected Assists (xA)", f"{match_data['Expected Assists (xA)']:.1f}"],
        ["HMLD (km)", f"{match_data['High Metabolic Load Distance (HMLD)']}"],
        ["Evaluations", match_data.get('Player Evaluations', '')]
    ]
    player_table = Table(player_data)
    player_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(player_table)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Tactical Analysis", styles['Heading2']))
    elements.append(Paragraph(f"Formation: {match_data['Formation']}", styles['Normal']))
    elements.append(Paragraph(f"Possession Zones: {match_data['Possession Zones']}", styles['Normal']))
    elements.append(Paragraph(f"Set Pieces: {match_data['Set Piece Outcomes']}", styles['Normal']))
    elements.append(Paragraph(f"Key Moments: {match_data['Notes']}", styles['Normal']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Recommendations", styles['Heading2']))
    recommendations = f"Adjust pressing (PPDA: {match_data['PPDA']}). Focus on {match_data['Possession Zones']}. Improve tackle success ({tackle_success:.1f}%)."
    elements.append(Paragraph(recommendations, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Add heatmap
    heatmap_fig = generate_heatmap(match_data.get("Formation Positions", ""))
    heatmap_fig.savefig("heatmap.png")
    elements.append(Paragraph("Player Heatmap", styles['Heading2']))
    elements.append(Image("heatmap.png", width=400, height=300))

    doc.build(elements)
    return pdf_path

# Email notification (optional)
def send_email(subject, body, recipients, pdf_path):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = st.secrets["email"]["sender"]
        msg['To'] = ", ".join(recipients)
        msg.attach(MIMEText(body, 'plain'))
        with open(pdf_path, "rb") as f:
            part = MIMEApplication(f.read(), Name="match_report.pdf")
            part['Content-Disposition'] = 'attachment; filename="match_report.pdf"'
            msg.attach(part)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(st.secrets["email"]["sender"], st.secrets["email"]["password"])
            server.sendmail(st.secrets["email"]["sender"], recipients, msg.as_string())
        st.success("Email sent!")
    except Exception as e:
        st.error(f"Email failed: {e}")

# Single tab for match input and report
st.subheader("Enter Match Data and Generate Report")

with st.form("match_form"):
    # Match details
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Match Date")
        opponent = st.text_input("Opponent Team")
        venue = st.selectbox("Venue", ["Home", "Away"])
    with col2:
        formation = st.text_input("Formation (e.g., 4-4-2)")
        weather = st.text_input("Weather (e.g., Sunny, Rain)")

    # Team stats
    st.write("**Team Stats**")
    col3, col4 = st.columns(2)
    with col3:
        our_score = st.number_input("Our Score", min_value=0, step=1)
        possession = st.number_input("Possession (%)", min_value=0, max_value=100, step=1)
        shots = st.number_input("Shots", min_value=0, step=1)
        shots_on_target = st.number_input("Shots on Target", min_value=0, step=1)
        passes_attempted = st.number_input("Passes Attempted", min_value=0, step=1)
        passes_completed = st.number_input("Passes Completed", min_value=0, step=1)
    with col4:
        corners = st.number_input("Corners", min_value=0, step=1)
        free_kicks = st.number_input("Free Kicks", min_value=0, step=1)
        offsides = st.number_input("Offsides", min_value=0, step=1)
        fouls_committed = st.number_input("Fouls Committed", min_value=0, step=1)
        fouls_suffered = st.number_input("Fouls Suffered", min_value=0, step=1)

    col5, col6 = st.columns(2)
    with col5:
        yellow_cards = st.number_input("Yellow Cards", min_value=0, step=1)
        red_cards = st.number_input("Red Cards", min_value=0, step=1)
    with col6:
        throw_ins = st.number_input("Throw-Ins", min_value=0, step=1)
        goal_kicks = st.number_input("Goal Kicks", min_value=0, step=1)

    # Attempt tracking
    st.write("**Attempt Tracking**")
    col9, col10 = st.columns(2)
    with col9:
        tackles_successful = st.number_input("Tackles Successful", min_value=0, step=1)
        tackles_attempted = st.number_input("Tackles Attempted", min_value=0, step=1)
        dribbles_successful = st.number_input("Dribbles Successful", min_value=0, step=1)
        dribbles_attempted = st.number_input("Dribbles Attempted", min_value=0, step=1)
    with col10:
        crosses_successful = st.number_input("Crosses Successful", min_value=0, step=1)
        crosses_attempted = st.number_input("Crosses Attempted", min_value=0, step=1)

    # Advanced metrics
    st.write("**Advanced Metrics**")
    col7, col8 = st.columns(2)
    with col7:
        xg = st.number_input("Expected Goals (xG)", min_value=0.0, step=0.1, value=shots_on_target * 0.1)
        xa = st.number_input("Expected Assists (xA)", min_value=0.0, step=0.1)
        xt = st.number_input("Expected Threat (xT)", min_value=0.0, step=0.1)
        ppda = st.number_input("Passes per Defensive Action (PPDA)", min_value=0.0, step=0.1)
    with col8:
        progressive_passes = st.number_input("Progressive Passes", min_value=0, step=1)
        line_breaking_passes = st.number_input("Line-Breaking Passes", min_value=0, step=1)
        field_tilt = st.number_input("Field Tilt (%)", min_value=0, max_value=100, step=1)
        hmld = st.number_input("High Metabolic Load Distance (km)", min_value=0.0, step=0.1)

    sca = st.number_input("Shot-Creating Actions (SCA)", min_value=0, step=1)
    gca = st.number_input("Goal-Creating Actions (GCA)", min_value=0, step=1)
    possession_zones = st.text_input("Possession Zones (e.g., Defensive:30%, Midfield:50%, Attacking:20%)")
    opponent_xg = st.number_input("Opponent Expected Goals (xG)", min_value=0.0, step=0.1)
    set_piece_outcomes = st.text_input("Set Piece Outcomes (e.g., Corner:Goal, Free Kick:Shot)")

    # Player stats
    st.write("**Player Stats**")
    player_goals = st.text_input("Goals (e.g., Player1, Player2)")
    player_assists = st.text_input("Assists (e.g., Player3)")
    player_shots = st.text_input("Shots (e.g., Player1, Player4)")
    player_minutes = st.text_input("Minutes Played (e.g., Player1:90, Player2:45)")
    player_evals = st.text_area("Player Evaluations (e.g., Player1: Passing 8/10)")

    # Tactical diagram
    st.write("**Tactical Diagram**")
    formation_positions = st.text_input("Formation Positions (e.g., Player1:ST,10,20)")

    # Notes and analysis
    notes = st.text_area("Notes (e.g., tactics, injuries)")
    opponent_score = st.number_input("Opponent Score", min_value=0, step=1)
    email_recipients = st.text_input("Email Results To (comma-separated emails, optional)")
    submitted = st.form_submit_button("Generate Report")

    if submitted:
        if shots_on_target > shots:
            st.error("Shots on target cannot exceed total shots.")
        elif passes_completed > passes_attempted:
            st.error("Passes completed cannot exceed passes attempted.")
        elif tackles_successful > tackles_attempted:
            st.error("Successful tackles cannot exceed attempted tackles.")
        elif dribbles_successful > dribbles_attempted:
            st.error("Successful dribbles cannot exceed attempted dribbles.")
        elif crosses_successful > crosses_attempted:
            st.error("Successful crosses cannot exceed attempted crosses.")
        else:
            pass_completion = (passes_completed / passes_attempted * 100) if passes_attempted > 0 else 0
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            match_data = {
                "Timestamp": timestamp,
                "Date": date.strftime("%Y-%m-%d"),
                "Opponent": opponent,
                "Venue": venue,
                "Formation": formation,
                "Weather": weather,
                "Our Score": our_score,
                "Opponent Score": opponent_score,
                "Possession (%)": possession,
                "Shots": shots,
                "Shots on Target": shots_on_target,
                "Passes Attempted": passes_attempted,
                "Passes Completed": passes_completed,
                "Corners": corners,
                "Free Kicks": free_kicks,
                "Offsides": offsides,
                "Fouls Committed": fouls_committed,
                "Fouls Suffered": fouls_suffered,
                "Yellow Cards": yellow_cards,
                "Red Cards": red_cards,
                "Throw-Ins": throw_ins,
                "Goal Kicks": goal_kicks,
                "Player Goals": player_goals,
                "Player Assists": player_assists,
                "Player Shots": player_shots,
                "Player Passes": "",
                "Player Tackles": "",
                "Player Interceptions": "",
                "Player Dribbles": player_minutes,
                "Player Distance (km)": "",
                "Player Sprints": "",
                "Player Minutes": player_minutes,
                "Notes": notes,
                "Expected Goals (xG)": xg,
                "Opponent Expected Goals (xG)": opponent_xg,
                "Pass Completion (%)": pass_completion,
                "Possession Zones": possession_zones,
                "Expected Assists (xA)": xa,
                "Expected Threat (xT)": xt,
                "PPDA": ppda,
                "Progressive Passes": progressive_passes,
                "Line-Breaking Passes": line_breaking_passes,
                "Field Tilt (%)": field_tilt,
                "High Metabolic Load Distance (HMLD)": hmld,
                "Shot-Creating Actions (SCA)": sca,
                "Goal-Creating Actions (GCA)": gca,
                "Set Piece Outcomes": set_piece_outcomes,
                "Tackles Successful": tackles_successful,
                "Tackles Attempted": tackles_attempted,
                "Dribbles Successful": dribbles_success,
                "Dribbles Attempted": dribbles_attempted,
                "Crosses Successful": crosses_successful,
                "Crosses Attempted": crosses_attempted,
                "Formation Positions": formation_positions,
                "Player Evaluations": player_evals
            }
            st.session_state.match_data = match_data

            # Generate PDF
            pdf_path = generate_pdf_report(match_data)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="Download Match Report PDF",
                    data=f,
                    file_name="match_report.pdf",
                    mime="application/pdf"
                )

            # CSV download
            df = pd.DataFrame([match_data])
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Match Data as CSV",
                data=csv,
                file_name="match_data.csv",
                mime="text/csv"
            )

            # Email report (optional)
            if email_recipients:
                body = f"Match Summary\nTimestamp: {timestamp}\nDate: {date}\nOpponent: {opponent}\nScore: {our_score}-{opponent_score}\nNotes: {notes}"
                send_email("Match Report", body, email_recipients.split(","), pdf_path)

            st.success("Report generated successfully!")
