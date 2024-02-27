from logging import Logger, INFO, StreamHandler, FileHandler, Formatter
from motor.motor_asyncio import AsyncIOMotorClient


def createLogger(name: str = "discord", level: int = INFO) -> Logger:
    logger = Logger(
        name=name,
        level=level,
    )
    formatter = Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    streamHandler = StreamHandler()
    streamHandler.setLevel(level)
    streamHandler.setFormatter(formatter)
    fileHandler = FileHandler(f"{name}.log")
    fileHandler.setLevel(INFO)
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    logger.addHandler(fileHandler)
    return logger


def getDatabase(url: str = "mongodb://localhost:27017/", name: str = "ART"):
    return AsyncIOMotorClient(url).get_database(name)
