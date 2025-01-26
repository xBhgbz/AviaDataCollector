import os


class ContractRabbitMQConfig:
    RMQ_USER = os.getenv("RABBITMQ_DEFAULT_USER")
    RMQ_PASS = os.getenv("RABBITMQ_DEFAULT_PASS")
    RMQ_HOST = os.getenv("RMQ_HOST")
    RMQ_PORT = os.getenv("RMQ_PORT")
    RMQ_EXCHANGE = os.getenv("RMQ_EXCHANGE", "")
    RMQ_ROUTING_KEY = os.getenv("RMQ_ROUTING_KEY")
    NEURO_CONTRACT_RMQ_ROUTING_KEY = os.getenv("NEURO_CONTRACT_RMQ_ROUTING_KEY")
    NEURO_CONTRACT_RESPONSE_RMQ_ROUTING_KEY = os.getenv("NEURO_CONTRACT_RESPONSE_RMQ_ROUTING_KEY")


class PsqlConfig:
    CONTACT_DB = os.getenv("CONTRACT_DB")
    CONTRACT_POSTGRES_USER = os.getenv("CONTRACT_POSTGRES_USER")
    CONTRACT_POSTGRES_PASSWORD = os.getenv("CONTRACT_POSTGRES_PASSWORD")
    CONTRACT_POSTGRES_HOST = os.getenv("CONTRACT_POSTGRES_HOST")
    CONTRACT_POSTGRES_PORT = os.getenv("CONTRACT_POSTGRES_PORT")


contract_rmq_config = ContractRabbitMQConfig()
psql_config = PsqlConfig()
