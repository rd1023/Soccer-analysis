# Mock AI-generated match summary
def generate_summary(events):
    summary = []
    total_shots = sum(1 for e in events if e["Event Type"] == "Shot")
    goals = sum(1 for e in events if e["Event Type"] == "Goal")
    xg_total = sum(e.get("xG", 0) for e in events if e["Event Type"] == "Shot")

    summary.append(f"Total shots taken: {total_shots}")
    summary.append(f"Goals scored: {goals}")
    summary.append(f"Total expected goals (xG): {xg_total:.2f}")

    if xg_total > 1.5 and goals == 0:
        summary.append("Underperformed on finishing. Consider finishing drills.")
    elif goals > xg_total:
        summary.append("Overperformed expected goals — high conversion rate.")
    else:
        summary.append("xG aligns with finishing results.")

    return "\n".join(summary)
