import pandas as pd

def create_event(event_type, timestamp, player=None, location=None, notes=None):
    return {
        "Event Type": event_type,
        "Timestamp": timestamp,
        "Player": player,
        "Location": location,
        "Notes": notes
    }

def save_events(event_list, filepath="output/reports/tagged_events.csv"):
    df = pd.DataFrame(event_list)
    df.to_csv(filepath, index=False)
