from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Lulu Analysis Match Report', 0, 1, 'C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 10, body)
        self.ln()

def generate_pdf_report(events, filename="output/reports/match_report.pdf"):
    pdf = PDF()
    pdf.add_page()
    pdf.chapter_title("Event Summary")
    for e in events:
        line = f"{e['Timestamp']}s - {e['Event Type']} by #{e['Player']}: {e['Notes']}"
        pdf.chapter_body(line)
    pdf.output(filename)
