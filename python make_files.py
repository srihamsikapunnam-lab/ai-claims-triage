from fpdf import FPDF

# Common Data
content_text = """
MEDICAL CLAIM REPORT
-------------------
Patient Name: Hasitha N
Date: 2023-10-27
Diagnosis: Viral Fever
Treatment: Consultation & Medication
Total Amount: 500
Status: Submitted
"""

def create_txt():
    with open("test_claim.txt", "w") as f:
        f.write(content_text)
    print("✅ Created test_claim.txt")

def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Split text by newlines and write to PDF
    for line in content_text.split('\n'):
        pdf.cell(200, 10, txt=line, ln=1, align='L')
        
    pdf.output("test_claim.pdf")
    print("✅ Created test_claim.pdf")

if __name__ == "__main__":
    create_txt()
    create_pdf()