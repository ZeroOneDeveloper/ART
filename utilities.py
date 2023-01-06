from logging import Logger, Formatter, StreamHandler, FileHandler


def getLogger(name: str, level: int) -> Logger:
    logger = Logger(name=name, level=level)
    formatter = Formatter('[%(asctime)s] [%(levelname)s] %(name)s: %(message)s')

    streamHandler = StreamHandler()
    fileHandler = FileHandler(filename=f'{name}.log', mode='a', encoding='utf-8')

    streamHandler.setFormatter(fmt=formatter)
    fileHandler.setFormatter(fmt=formatter)

    streamHandler.setLevel(level)
    fileHandler.setLevel(level)

    logger.addHandler(streamHandler)
    logger.addHandler(fileHandler)

    return logger
