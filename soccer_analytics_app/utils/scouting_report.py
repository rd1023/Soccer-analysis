from fpdf import FPDF

class ScoutingPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Scouting Report - Lulu Analysis', 0, 1, 'C')
        self.ln(10)

    def section_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)

    def section_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 10, body)
        self.ln()

def generate_scouting_report(events, filename="output/reports/scouting_report.pdf"):
    pdf = ScoutingPDF()
    pdf.add_page()
    pdf.section_title("Key Events")
    for e in events:
        line = f"{e['Timestamp']}s - {e['Event Type']} by #{e['Player']}: {e['Notes']}"
        pdf.section_body(line)
    pdf.output(filename)
