import os


class RabbitMQConfig:
    RMQ_USER = os.getenv("RABBITMQ_DEFAULT_USER")
    RMQ_PASS = os.getenv("RABBITMQ_DEFAULT_PASS")
    RMQ_HOST = os.getenv("RMQ_HOST")
    RMQ_PORT = os.getenv("RMQ_PORT")
    RMQ_EXCHANGE = os.getenv("RMQ_EXCHANGE", "")
    RMQ_ROUTING_KEY = os.getenv("RMQ_ROUTING_KEY")
    BATCH_SIZE = os.getenv("BATCH_SIZE")


rmq_config = RabbitMQConfig()
