from datetime import datetime

from pydantic import BaseModel
from typing import List, Dict


class ContractDataModel(BaseModel):
    site_url: str
    tender_info_link: str | None
    tender_number: str
    purchase_object: str | None
    customer: str | None = None
    price: float | None = None
    documents_info: List[Dict] | None = None
    amount_parsed_files: int = 0

    class Config:
        orm_mode = True


class ContractForAdminModel(BaseModel):
    site_url: str
    tender_info_link: str | None
    tender_number: str
    purchase_object: str | None
    customer: str | None = None
    price: float | None = None

    class Config:
        orm_mode = True


class GetFieldContractData(BaseModel):
    site_url: str
    tender_number: str
