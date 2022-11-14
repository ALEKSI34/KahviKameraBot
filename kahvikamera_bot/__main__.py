
from .bot import botti_idle
from loguru import logger

def main():
    logger.info("Starting Bot")
    botti_idle()


if __name__ == "__main__":
    main()