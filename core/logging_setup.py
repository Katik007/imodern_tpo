"""Настройка логирования DEBUG / INFO / WARN / ERROR."""

from __future__ import annotations

import logging
import sys

from core.config import ROOT_DIR, settings

_CONFIGURED = False


def setup_logging(level: str | None = None) -> logging.Logger:
    global _CONFIGURED
    log_level = getattr(logging, (level or settings.log_level).upper(), logging.INFO)
    logger = logging.getLogger("autotest")
    logger.setLevel(log_level)

    if _CONFIGURED:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s:%(lineno)d — %(message)s",
        datefmt="%H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(log_level)
    console.setFormatter(formatter)

    logs_dir = ROOT_DIR / "logs"
    logs_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(logs_dir / "autotest.log", mode="w", encoding="utf-8")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(log_level)
    root.addHandler(console)
    root.addHandler(file_handler)

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    _CONFIGURED = True
    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    setup_logging()
    return logging.getLogger(name or "autotest")
