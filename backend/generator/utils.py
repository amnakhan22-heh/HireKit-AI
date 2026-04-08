import pypdf


def extract_text_from_pdf(file_object) -> str:
    reader = pypdf.PdfReader(file_object)
    text = ''
    for page in reader.pages:
        text += page.extract_text() or ''
    if not text.strip():
        raise ValueError(
            "Could not extract text from the PDF. The file may be scanned or unreadable."
        )
    return text
