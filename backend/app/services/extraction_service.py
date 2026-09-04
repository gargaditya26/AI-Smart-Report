import PyPDF2
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
from docx import Document
import io
import re
from typing import Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextExtractionService:
    """Service for extracting text from various file formats"""

    @staticmethod
    def extract_from_pdf(file_content: bytes) -> Tuple[str, bool]:
        """
        Extract text from PDF file
        Returns: (extracted_text, used_ocr)
        """
        try:
            # Try direct text extraction first
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

            # If text extraction yields minimal content, use OCR
            if len(text.strip()) < 100:
                return TextExtractionService._ocr_from_pdf(file_content), True

            return text, False
        except Exception as e:
            print(f"PDF extraction error: {e}")
            # Fallback to OCR
            return TextExtractionService._ocr_from_pdf(file_content), True

    @staticmethod
    def _ocr_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF using OCR"""
        try:
            images = convert_from_bytes(file_content)
            text = ""
            for image in images:
                text += pytesseract.image_to_string(image) + "\n"
            return text
        except Exception as e:
            print(f"OCR error: {e}")
            return ""

    @staticmethod
    def extract_from_image(file_content: bytes) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(io.BytesIO(file_content))
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"Image OCR error: {e}")
            return ""

    @staticmethod
    def extract_from_docx(file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(io.BytesIO(file_content))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            print(f"DOCX extraction error: {e}")
            return ""

    @staticmethod
    def extract_from_txt(file_content: bytes) -> str:
        """Extract text from TXT file"""
        try:
            return file_content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return file_content.decode('latin-1')
            except Exception as e:
                print(f"TXT extraction error: {e}")
                return ""

    @staticmethod
    def extract_text(file_content: bytes, file_type: str) -> Tuple[str, str]:
        """
        Main method to extract text from file
        Returns: (extracted_text, extraction_method)
        """
        logger.info("=" * 80)
        logger.info("TEXT EXTRACTION STARTED")
        logger.info(f"File type: {file_type}")
        logger.info(f"File size: {len(file_content)} bytes")

        file_type = file_type.lower()

        if file_type == 'pdf' or file_type == 'application/pdf':
            text, used_ocr = TextExtractionService.extract_from_pdf(file_content)
            method = "OCR" if used_ocr else "Direct PDF extraction"
            logger.info(f"Extraction method: {method}")
            logger.info(f"Extracted text length: {len(text)} characters")
            logger.info(f"First 1000 characters:\n{text[:1000]}")
            return text, method

        elif file_type in ['jpg', 'jpeg', 'png', 'image/jpeg', 'image/png']:
            text = TextExtractionService.extract_from_image(file_content)
            logger.info(f"Extraction method: OCR (image)")
            logger.info(f"Extracted text length: {len(text)} characters")
            logger.info(f"First 1000 characters:\n{text[:1000]}")
            return text, "OCR"

        elif file_type in ['docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            text = TextExtractionService.extract_from_docx(file_content)
            logger.info(f"Extraction method: DOCX")
            logger.info(f"Extracted text length: {len(text)} characters")
            logger.info(f"First 1000 characters:\n{text[:1000]}")
            return text, "DOCX extraction"

        elif file_type in ['txt', 'text/plain']:
            text = TextExtractionService.extract_from_txt(file_content)
            logger.info(f"Extraction method: Text file")
            logger.info(f"Extracted text length: {len(text)} characters")
            logger.info(f"First 1000 characters:\n{text[:1000]}")
            return text, "Text file"

        else:
            logger.error(f"Unsupported file format: {file_type}")
            return "", "Unsupported format"

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize extracted text"""
        # Preserve line breaks: pathology reports use rows, and the analysis
        # parser relies on those rows to distinguish test names from metadata.
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        cleaned_lines = []
        for line in text.split("\n"):
            line = re.sub(r"[ \t]+", " ", line).strip()
            line = re.sub(r"[^\w\s\.\,\:\;\-\(\)\/\%\<\>&µμ]+", "", line)
            if line:
                cleaned_lines.append(line)
        return "\n".join(cleaned_lines).strip()
