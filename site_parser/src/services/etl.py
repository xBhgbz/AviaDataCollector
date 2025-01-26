import random

from loguru import logger

from services.parser import WebParser
from services.producer import MQProducer
from services.scraper import WebScraper

from tools import timer

logger.add("info.log", format="Log: [{time} - {level} - {message}]", level="INFO", enqueue=True)


class ETL:
    """Класс обработки парсинга документов"""

    def __init__(
            self,
            scraper: WebScraper,
            parser: WebParser,
            producer: MQProducer,
            urls: list[str],
            date_start: str = None,
            date_finish: str = None
    ):
        self.scraper = scraper
        self.parser = parser
        self.producer = producer
        self.urls = urls
        self.date_start = date_start
        self.date_finish = date_finish

    @timer
    def load_data(self):
        logger.info("Start load data %s <-> %s" % (str(self.date_start), str(self.date_finish)))

        for url, tender_type in self.urls:
            logger.info("Process tenders for %s" % tender_type)
            count = 0
            html = self.scraper.get_html(url, self.date_start, self.date_finish, page=1)

            # сколько страниц нашлось для запроса
            amount_page = self.parser.get_page_number(html)

            for page in range(1, amount_page + 1):
                logger.info("Getting tenders list. Page %d / %d" % (page, amount_page))
                # получение основной информации и ссылки на вложения с доками
                html = self.scraper.get_html(url, self.date_start, self.date_finish, page)
                data_list = self.parser.parse_list_html(html, tender_type)
                self.scraper.sleeping(0.5 + random.random())

                count += len(data_list)

                for i in range(len(data_list)):
                    tender = data_list[i]
                    # вытаскиваем урлы документов тендера из ссылок вложения с доками
                    document_url = tender["documents_info"]
                    html = self.scraper.get_html(document_url)
                    documents_info: list[str] = self.parser.parse_document_html(html, tender_type)
                    tender["documents_info"] = documents_info

                    self.scraper.sleeping(0.5 + random.random())

                with self.producer.connect() as connection:
                    logger.info("Connected to RabbitMQ...")
                    with connection.channel() as channel:
                        logger.info("Publishing batch size message... % s" % data_list[0])
                        self.producer.batch_publish(channel=channel, data=data_list)

            logger.info("Total count tenders per url %s: %d" % (url, count))
