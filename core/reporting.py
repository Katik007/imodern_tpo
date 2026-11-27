"""Маскирование данных при сохранении результатов прогона."""

import json
import re
from pathlib import Path


def redact(text: str, private_values: list[str]) -> str:
    for value in sorted(filter(None, private_values), key=len, reverse=True):
        text = text.replace(value, "[скрыто]")
    return re.sub(r"(?i)([?&](?:sessid|token|sid)=)[^&\s]+", r"\1[скрыто]", text)


def publish_results(results: Path, summary: Path, private_values: list[str]) -> None:
    # Allure reads exception messages independently of pytest's formatted traceback.
    cases = []
    for path in results.glob("*-result.json"):
        result = json.loads(path.read_text(encoding="utf-8"))
        details = result.get("statusDetails", {})
        for key in ("message", "trace"):
            if key in details:
                details[key] = redact(details[key], private_values)
        if details:
            path.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
        status = result["status"]
        reason = details.get("message", "").removeprefix("Skipped: ").strip() if status == "skipped" else ""
        cases.append((result["name"], status, reason))

    passed = sum(status == "passed" for _, status, _ in cases)
    labels = {
        "passed": "Пройден",
        "failed": "Не пройден",
        "broken": "Ошибка выполнения",
        "skipped": "Пропущен",
    }
    rows = [
        f"| {name.replace('|', '&#124;')} | {labels.get(status, status)} | {reason.replace('|', '&#124;')} |"
        for name, status, reason in sorted(cases)
    ]
    summary.parent.mkdir(exist_ok=True)
    summary.write_text(
        "\n".join([
            "# Результаты последнего прогона",
            "",
            f"Пройдено **{passed} из {len(cases)}**.",
            "",
            "| Проверка | Статус | Причина пропуска |",
            "|---|---|---|",
            *rows,
            "",
            "[Подробный отчёт Allure](../allure-report/index.html)",
            "",
        ]),
        encoding="utf-8",
    )
