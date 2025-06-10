# Mock xG model function
def calculate_xg(event):
    if event['Event Type'] == 'Shot':
        # Simple rules for demo purposes
        if "box" in event.get("Location", "").lower():
            return 0.3
        else:
            return 0.1
    return 0
