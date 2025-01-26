import time
from typing import Protocol

import requests
from fake_useragent import UserAgent

from core.sites_config import GosZakupki

from tools import backoff


class WebScraper(Protocol):
    """Интерфейс для веб-скраперов."""

    def get_html(self, url: str, date_start: str = None, date_finish: str = None, page: int = None) -> str:
        """Получает страницу со списками тендеров."""
        ...

    @staticmethod
    def sleeping(sec: float):
        """Засывает на sec секунд"""


class BaseWebScraperService:
    """Базовый класс обработки url"""

    def __init__(self, config):
        self.config = config

    @staticmethod
    def _get_url_with_params(base_url: str, *args):
        """Добавляет к url парамсы"""
        for arg in args:
            if arg:
                base_url += arg
        return base_url

    @staticmethod
    @backoff()
    def _get_html(url: str) -> str | None:
        """Получает страницу со списками тендеров"""

        headers = {"User-Agent": UserAgent().chrome, "Connection": "keep-alive"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return response.text

    @staticmethod
    def sleeping(sec: float):
        """Засывает на sec секунд"""
        time.sleep(sec)


class GosZakupkiWebScraper(BaseWebScraperService):
    """Класс обработки url для сайта https://zakupki.gov.ru/"""

    def __init__(self, config: GosZakupki):
        super().__init__(config)

    def get_html(
            self,
            url: str,
            date_start: str = None,
            date_finish: str = None,
            page: int = None
    ) -> str:
        """Получает страницу со списками тендеров"""

        page = self.config.get_page(page)
        date_start = self.config.get_start_date(date_start)
        date_finish = self.config.get_finish_date(date_finish)

        base_url = self._get_url_with_params(url, page, date_start, date_finish)
        return self._get_html(base_url)
