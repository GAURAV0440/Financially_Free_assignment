import logging
from pathlib import Path

def get_logger(name: str = "vahan"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        logger.addHandler(ch)
    return logger

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)
