import json
import random
import time
from typing import Protocol


import requests
from loguru import logger
from requests import Response

from constants import DOWNLOAD_PATH, AVIA_PROMPT, CONTRACT_PROMT, CHAT_URL, STATUS_URL, STATUS_HEADERS, CHAT_HEADERS
from services.neuro_parsing import _merge_data, _parse_ai_response
from tools import backoff


class BaseNeuroStream(Protocol):

    def neuro_chat(self) -> str:
        """Подготавливает сообщения для нейросети, разбивает на батчи"""
        pass

    def ai_api(self, message: str) -> str:
        """Предоставляет апи общения с нейросетью"""


class NeuroDuckDuckGo:

    def __init__(self):
        self.messages = []
        self.status = None
        self.model = "gpt-4o-mini"
        self.status_url = STATUS_URL
        self.chat_url = CHAT_URL
        self.new_vqd = None
        self.status_headers = STATUS_HEADERS
        self.chat_headers = CHAT_HEADERS

    @staticmethod
    def _sleep():
        time.sleep(10 + random.randint(5, 15))

    @staticmethod
    def _get_neuro_message_structure(content: str, role: str) -> dict:
        """
        Отдает структуру сообщения для следующего запроса в нейронку

        :param str content: само сообщение
        :param str role: тот, кто присылал. Либо user либо role
        """

        return {"content": content, "role": role}

    def neuro_chat(self, path: str = DOWNLOAD_PATH, batch_size: int = 13000) -> dict:
        """Подготавливает сообщения для нейросети, разбивает на батчи"""
        logger.info("Start processed neuro chat...")
        self._sleep()

        self.init_chat()
        
        try:
            logger.info("Start fetchong AVIA_PROMPT")
            self.process_fetch(AVIA_PROMPT)
            logger.info("End fetchong AVIA_PROMPT")
            self._sleep()
            
            with open(path, "r") as f:
                chunk = f.read(batch_size)
                while chunk:
                    logger.info("Chunck: %s" % chunk)
                    logger.info("Start fetching chunk!")
                    self.process_fetch(chunk + ". Это еще не конец. Отвечай после моего сообщения: 'Теперь отвечай'")
                    logger.info("End fetching chunk!")
                    chunk = f.read(batch_size)
                    self._sleep()

            logger.info("Start fetching avia_data_response!")
            avia_data_response = self.process_fetch("Теперь отвечай.")
            logger.info("End fetching avia_data_response!")

            self._sleep()
            logger.info("Start fetching contract_data_response!")
            contract_data_response = self.process_fetch(CONTRACT_PROMT)
            logger.info("End fetching contract_data_response!")

        except RuntimeError:
            logger.error("Runtime in parsing!")
            raise

        logger.info("avia_data_response: %s" % avia_data_response)
        logger.info("contract_data_response: %s" % contract_data_response)

        return _merge_data(avia_data_response, contract_data_response)

    def init_chat(self):
        """Инициализация чата с нейронкой"""
        self.fetch_status()
        logger.info("Init chat. vqd: %s" % self.new_vqd)
        if not self.new_vqd:
            logger.error("Problem with x-vqd-4")
            raise ValueError("Problem with x-vqd-4")

    def fetch_status(self) -> None:
        """Получение X-Vqd-4"""

        response = requests.get(self.status_url, headers={"x-vqd-accept": "1"})
        logger.info("Status response code %d" % response.status_code)
        self.new_vqd = response.headers.get("x-vqd-4")

    @backoff(exceptions=(requests.RequestException,))
    def fetch(self, content: str) -> Response:
        """Отправка сообщения нейронке"""
        logger.info("Start fetching...")

        self.messages.append(self._get_neuro_message_structure(content, "user"))

        payload: dict = {"model": self.model, "messages": self.messages}
        headers: dict = {"x-vqd-4": self.new_vqd, "Content-Type": "application/json"}
        response: Response = requests.post(self.chat_url, headers=headers, data=json.dumps(payload))
        logger.info("Status: %s" % response.status_code)

        if response.status_code == 429:
            logger.error("429")
            raise requests.RequestException

        return response

    def process_fetch(self, content: str) -> str:
        """Полная обработка запроса"""
        logger.info("Start process_fetch...")

        response: Response = self.fetch(content)
        full_message: str = _parse_ai_response(response)
        logger.info("Full message: %s" % full_message)

        self.last_vqd = self.new_vqd
        self.new_vqd = response.headers.get("x-vqd-4")

        self.messages.append(self._get_neuro_message_structure(full_message, "assistant"))
        return full_message

        