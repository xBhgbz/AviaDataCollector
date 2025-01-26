import os
import re
import time
from typing import Generator, Protocol

import backoff
from fake_useragent import UserAgent
import textract
import requests
from loguru import logger

from constants import DOC_PATH, DOWNLOAD_PATH, DOC_SIZE_LIMIT


class BaseDocHandler(Protocol):
    """Интерфейс для класса обработчика Документа"""

    def process_document(self, url: str, file_name: str, ext: str = None) -> None:
        """Скачивает документ тендера по ссылке и достает содержимое в .txt формате"""

    def parse_document(self, doc_name: str) -> None:
        """Парсит документ"""


class DocHandler:

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5)
    def process_document(self, url: str, file_name: str, ext: str) -> None:
        """Скачивает документ тендера по ссылке"""

        logger.info("Start proccess document..")
        extension = ext
        output_path = os.path.join(DOC_PATH, f"download.{extension}")

        headers = {"User-Agent": UserAgent().chrome, "Connection": "keep-alive"}
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()

        with open(output_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        logger.info("File success downloaded! Path: %s" % output_path)
        self.parse_document(output_path, ext)

    def parse_document(self, output_path: str, ext: str) -> None:
        """Парсит документ"""
        logger.info("Parsing documents...")

        text = textract.process(output_path)

        if ext == "pdf" and not text.strip():
            # проверим, если был пдф, то возможно текст отсканирован
            text = textract.process(output_path, method="tesseract", language="rus+rus")
        decoded_text = self.clean_text(text.decode("utf-8"))

        with open(DOWNLOAD_PATH, "w", encoding="utf-8") as f:
            f.write(decoded_text)

        if len(decoded_text) > DOC_SIZE_LIMIT:
            raise IOError("Размер файла превышает заложенный лимит в %d" % DOC_SIZE_LIMIT)

    @staticmethod
    def clean_text(text: str) -> str:
        """Удаляет лишние переносы строк и лишние пробелы"""
        cleaned_text = re.sub(r"\n\s*\n", "\n", text.strip())
        cleaned_text = re.sub(r"[ \t]+", " ", cleaned_text)
        return cleaned_text

#
# dc = DocHandler()
# # dc.process_document("https://zakupki.gov.ru/44fz/filestore/public/1.0/download/priz/file.html?uid=06EA0C3AE3854902852A2B80FD7A1E47", "Проект контракта.docx")
# dc.parse_document("1.docx")
