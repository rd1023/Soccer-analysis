def save_coach_notes(text, filename="notes/coach_notes.txt"):
    with open(filename, "w") as f:
        f.write(text)
