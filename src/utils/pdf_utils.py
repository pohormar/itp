import fitz  # PyMuPDF
from io import BytesIO
from xhtml2pdf import pisa
import re
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def extract_text_from_pdf(pdf_bytes):
    """Wyciąga surowy tekst z bajtów pliku PDF."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = "".join(page.get_text() for page in doc)
        doc.close()
        return text
    except Exception as e:
        return f"Błąd podczas odczytu pliku PDF: {e}"

def create_pdf_from_html(html_content: str) -> bytes:
    """Generuje plik PDF z tekstu HTML używając xhtml2pdf i dołączonej czcionki."""

    base_dir = Path(__file__).resolve().parents[2]
    font_regular_path = base_dir / "assets" / "fonts" / "NotoSans-Regular.ttf"

    # Nie musimy już ręcznie rejestrować czcionki w reportlab,
    # ponieważ @font-face w CSS zrobi to za nas w bardziej niezawodny sposób.

    # Stwórz CSS, który definiuje i używa naszej czcionki.
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @font-face {{
                font-family: 'NotoSans';
                src: url('{font_regular_path}');
            }}
            body {{
                font-family: 'NotoSans', sans-serif;
                line-height: 1.6;
            }}
            h1, h2, h3, h4, h5, h6, b, strong {{
                font-weight: bold; /* Przeglądarka/generator sam obsłuży pogrubienie */
            }}
            h1 {{
                font-size: 24px;
            }}
             h2 {{
                font-size: 20px;
            }}
            h3, h4, h5, h6 {{
                font-size: 16px;
            }}
            p {{
                font-size: 14px;
                margin-bottom: 10px;
                font-weight: normal;
            }}
            ul, ol {{
                padding-left: 20px;
            }}
            li {{
                 margin-bottom: 5px;
            }}
            code {{
                background-color: #f4f4f4;
                padding: 2px 4px;
                border-radius: 4px;
                font-family: monospace;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    result = BytesIO()
    
    pisa_status = pisa.CreatePDF(
        BytesIO(full_html.encode("UTF-8")),
        dest=result,
        encoding='UTF-8'
    )

    if pisa_status.err:
        raise Exception(f"Błąd podczas generowania PDF: {pisa_status.err}")

    return result.getvalue() 