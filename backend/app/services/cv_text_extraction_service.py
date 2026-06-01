from pathlib import Path

import fitz
from docx import Document
from fastapi import UploadFile


SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx"}


class UnsupportedFileTypeError(ValueError):
    pass


class EmptyExtractedTextError(ValueError):
    pass


async def extract_text_from_upload(file: UploadFile) -> str:
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            f"Unsupported file type: {extension or 'unknown'}"
        )

    file_bytes = await file.read()

    if extension == ".txt":
        text = extract_text_from_txt(file_bytes)
    elif extension == ".pdf":
        text = extract_text_from_pdf(file_bytes)
    elif extension == ".docx":
        text = extract_text_from_docx(file_bytes)
    else:
        raise UnsupportedFileTypeError(
            f"Unsupported file type: {extension}"
        )

    cleaned_text = clean_extracted_text(text)

    if not cleaned_text:
        raise EmptyExtractedTextError("No text could be extracted from the file.")

    return cleaned_text


def extract_text_from_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text_parts: list[str] = []

    with fitz.open(stream=file_bytes, filetype="pdf") as document:
        for page in document:
            text_parts.append(page.get_text())

    return "\n".join(text_parts)


def extract_text_from_docx(file_bytes: bytes) -> str:
    from io import BytesIO

    document = Document(BytesIO(file_bytes))

    paragraphs = [
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    return "\n".join(paragraphs)


def clean_extracted_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    non_empty_lines = [line for line in lines if line]

    return "\n".join(non_empty_lines)
