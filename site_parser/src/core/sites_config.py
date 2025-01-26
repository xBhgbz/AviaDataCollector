import os


class GosZakupki:
    base_url: str = os.getenv("ZAKUPKI_BASE_URL", "https://zakupki.gov.ru")

    page_number: str = os.getenv("ZAKUPKI_PAGE_NUMBER")
    publish_date_from: str = os.getenv("ZAKUPKI_PUBLISH_DATE_FROM")  # ДД.ММ.ГГГГ
    publish_date_to: str = os.getenv("ZAKUPKI_PUBLISH_DATE_TO")  # ДД.ММ.ГГГГ

    purchase_url: str = os.getenv("ZAKUPKI_PURCHASE_URL")
    purchase_detail_url: str = os.getenv("ZAKUPKI_PURCHASE_DETAIL_URL")
    purchase_documents_url: str = os.getenv("ZAKUPKI_PURCHASE_DOCUMENTS_URL")

    contract_url: str = os.getenv("ZAKUPKI_CONTRACT_URL")
    contract_detail_url: str = os.getenv("ZAKUPKI_CONTRACT_DETAIL_URL")
    contract_documents_info: str = os.getenv("ZAKUPKI_CONTRACT_DOCUMENTS_INFO")

    def get_page(self, page: int | None) -> str | None:
        if page:
            return self.page_number + str(page)
        return

    def get_start_date(self, date: str | None):
        if date:
            return self.publish_date_from + date
        return

    def get_finish_date(self, date: str | None):
        if date:
            return self.publish_date_to + date
        return


zakupki_config = GosZakupki()
