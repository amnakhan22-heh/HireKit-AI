import pypdf


def extract_text_from_pdf(file_object) -> str:
    """
    Extract all text from a PDF file object using pypdf.

    Iterates over every page and concatenates the extracted text. Raises
    ``ValueError`` if the extracted text is empty (e.g. scanned/image-only PDFs).

    Args:
        file_object: A file-like object opened in binary mode, typically from
            ``request.FILES`` in a Django view.

    Returns:
        str: The concatenated plain text from all pages.

    Raises:
        ValueError: If the PDF yields no extractable text.
    """
    reader = pypdf.PdfReader(file_object)
    text = ''
    for page in reader.pages:
        text += page.extract_text() or ''
    if not text.strip():
        raise ValueError(
            "Could not extract text from the PDF. The file may be scanned or unreadable."
        )
    return text
