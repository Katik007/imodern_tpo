"""Параметры и ожидаемые результаты сценариев."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AuthCase:
    case_id: str
    title: str
    identifier_kind: str
    identifier_data: str
    password_data: str
    expected_error: str | None = None
