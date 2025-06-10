# Recommend training topics based on performance gaps
def recommend_focus(stats):
    recs = []
    if stats.get("xG", 0) > 1.5 and stats.get("Goals", 0) < 1:
        recs.append("Finishing under pressure")
    if stats.get("Wide Entries", 0) < 3:
        recs.append("Wide area creation with overlaps and cutbacks")
    if stats.get("Pass %", 0) < 75:
        recs.append("Short passing under pressure")
    return recs
