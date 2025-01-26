from typing import Protocol

from bs4 import BeautifulSoup

from core.sites_config import GosZakupki


class WebParser(Protocol):
    """Интерфейс для веб-парсера."""

    def get_page_number(self, html: str) -> int:
        """Получает количество страниц со списками объектов"""

    def parse_list_html(self, html: str, type_: str):
        """Получает необходимые данные по списку тендеров"""

    def parse_document_html(self, html: str, type_: str):
        """Получает ссылуки документов тендеров"""


class ZakupkiBeautifulSoupParser:
    """Парсер для сервиса https://zakupki.gov.ru"""

    def __init__(self, config: GosZakupki):
        self.config = config

    def get_page_number(self, html: str) -> int:
        """Возвращает количество страниц"""
        soup = BeautifulSoup(html, "html.parser")
        page_blocks = soup.find_all("li", class_="page")
        if not page_blocks:
            return 1
        return int(page_blocks[-1].get_text(strip=True))

    def parse_list_html(self, html: str, type_: str):
        """Получает информацию о тендерах из списка"""

        soup = BeautifulSoup(html, "html.parser")
        blocks = soup.find_all("div", class_="registry-entry__form")
        data: list[dict] = []

        for i in range(len(blocks)):
            block = blocks[i]
            info = self.get_header_tender_info(block, type_)
            data.append(info)

        return data

    def parse_document_html(self, html: str, type_: str) -> list[dict]:
        """Получает ссылуки документов тендеров"""
        soup = BeautifulSoup(html, "html.parser")
        links: list = []

        if type_ == "contract":
            attachment = soup.find("div", class_="card-attachments__block")
            attachment_section = attachment.find("div", class_="b-left") if attachment else None
        else:
            attachment_section = soup.find("div", class_="blockFilesTabDocs")

        if attachment_section:
            for link in attachment_section.find_all("a", href=True, title=True):
                links.append(
                    {
                        "title": link["title"],
                        "link": link["href"],
                        "text": link.get_text(strip=True)
                    }
                )

        return links

    @staticmethod
    def parse_price(price: str) -> float:
        """Парсит цену тендера"""
        cleaned_price = price.strip().replace("\xa0", "").replace("₽", "").replace(" ", "")
        cleaned_price = cleaned_price.replace(",", ".")
        return float(cleaned_price)

    @staticmethod
    def base_parse(obj: str, type_: str) -> str:
        """Удаляет лишние пробелы и переносы строки"""
        value = obj.replace('\n', '')
        if type_ == "contract":
            value = value.replace(' ', '')
        return value

    def get_header_tender_info(self, block, type_) -> dict:
        """Получает ссылку на документы и основную информацию из карточек тендера в списке"""

        header = block.find("div", class_="registry-entry__header-mid__number")
        tender_info_url: str = header.find("a").get("href")
        tender_number: str = tender_info_url.split("=")[1]

        purchase_object: str = block.find("div", class_="registry-entry__body-value").get_text(strip=True)
        customer: str = block.find("div", class_="registry-entry__body-href").get_text(strip=True)

        price: str = block.find("div", class_="price-block__value").get_text()
        document_block = block.find_all("div", class_="href")[0]
        document_url: str = document_block.find("a").get("href") if document_block else None

        info = {
            "site_url": self.config.base_url,
            "tender_info_link": self.config.base_url + tender_info_url,
            "tender_number": tender_number,
            "purchase_object": self.base_parse(purchase_object, type_) if purchase_object else None,
            "customer": customer,
            "price": self.parse_price(price) if price else None,
            "documents_info": self.config.base_url + document_url
        }

        return info
