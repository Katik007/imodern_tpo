"""Настройки публичного прогона iModern."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    base_url: str = "https://imodern.ru"
    browser: str = os.getenv("BROWSER", "chromium").lower()
    headless: bool = os.getenv("HEADLESS", "true").lower() in {"1", "true", "yes"}
    show_steps: bool = os.getenv("IMODERN_SHOW_STEPS") == "1"
    default_timeout_ms: int = int(os.getenv("DEFAULT_TIMEOUT_MS", "20000"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
    email: str = os.getenv("IMODERN_TEST_EMAIL", "")
    phone: str = os.getenv("IMODERN_TEST_PHONE", "")
    password: str = os.getenv("IMODERN_TEST_PASSWORD", "")
    account_name: str = os.getenv("IMODERN_TEST_ACCOUNT_NAME", "")
    data_file: Path = Path(os.getenv("IMODERN_TEST_DATA", ROOT_DIR / "data" / "imodern.json"))

    @property
    def private_values(self) -> list[str]:
        values = [self.email, self.phone, self.password, self.account_name]
        digits = "".join(filter(str.isdigit, self.phone))
        if len(digits) == 11:
            prefix = f"+{digits[0]} ({digits[1:4]}) {digits[4:7]}"
            values.extend([digits, f"{prefix} {digits[7:]}", f"{prefix}-{digits[7:9]}-{digits[9:]}"])
        return values


settings = Settings()
