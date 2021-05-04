import logging

logger = logging.getLogger(__name__)


def prepare_logging(level):
    out_handler = logging.StreamHandler()
    logger.setLevel(level=level)
    out_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)-10s - [in %(filename)s:%(lineno)d]: - %(message)s'))
    logger.addHandler(out_handler)
