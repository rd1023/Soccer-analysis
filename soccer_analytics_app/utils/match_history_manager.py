import os

def list_match_reports(report_dir="output/reports"):
    return [f for f in os.listdir(report_dir) if f.endswith(".pdf") or f.endswith(".pptx")]
