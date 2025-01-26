from db.postgres import Base
from sqlalchemy import Column, String, Text, Float, JSON, DateTime, Integer, text, PrimaryKeyConstraint


class ContractData(Base):
    __tablename__ = "contract_data"

    site_url = Column(String(300))
    tender_info_link = Column(String(300))
    tender_number = Column(String(300))
    purchase_object = Column(Text)
    customer = Column(String(300), nullable=True)
    price = Column(Float, nullable=True)
    documents_info = Column(JSON, nullable=True)

    amount_parsed_files = Column(Integer, default=0)
    created_at = Column(DateTime, default=text("current_timestamp"))
    updated_at = Column(DateTime, default=text("current_timestamp"))

    __table_args__ = (
        PrimaryKeyConstraint("site_url", "tender_number", name="pk_site_url_tender_number"),
    )
