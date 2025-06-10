import pandas as pd

def generate_player_report(events_df, player_name):
    player_events = events_df[events_df["Player"] == player_name]
    summary = player_events.groupby("Event Type").size().reset_index(name="Count")
    return summary
