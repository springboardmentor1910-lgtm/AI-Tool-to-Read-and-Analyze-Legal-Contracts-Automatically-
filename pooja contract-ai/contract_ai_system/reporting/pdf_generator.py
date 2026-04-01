from fpdf import FPDF

class PDFGenerator:
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)

    def create_pdf(self, summary_text, filepath="report.pdf"):
        self.pdf.add_page()
        self.pdf.set_font("Arial", size=12)

        for line in summary_text.split("\n"):
            self.pdf.multi_cell(0, 6, line)

        self.pdf.output(filepath)
        return filepath
