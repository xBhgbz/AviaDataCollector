from datetime import date, timedelta

from celery import shared_task

from constants import URLS
from core.config import rmq_config
from core.sites_config import zakupki_config
from services.etl import ETL
from services.parser import ZakupkiBeautifulSoupParser
from services.producer import RabbitMQProducer
from services.scraper import GosZakupkiWebScraper


@shared_task
def extract_tender_task(date_start=None, date_finish=None):
    """Celery task для парсинга тендеров."""

    date_start = date_start or (date.today() - timedelta(weeks=4)).strftime('%d.%m.%Y')
    date_finish = date_finish or (date.today() - timedelta(weeks=4)).strftime('%d.%m.%Y')

    scraper = GosZakupkiWebScraper(zakupki_config)
    parser = ZakupkiBeautifulSoupParser(zakupki_config)
    producer = RabbitMQProducer(rmq_config)

    etl = ETL(scraper, parser, producer, URLS, date_start, date_finish)
    etl.load_data()
