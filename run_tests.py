"""Одна команда для запуска проверок iModern и формирования Allure."""

import argparse
import os
import subprocess
import sys
import webbrowser

from core.allure_cli import generate_report, prepare_allure
from core.config import ROOT_DIR, settings
from core.reporting import publish_results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--headed", action="store_true", help="показать шаги тестов в открытом браузере")
    parser.add_argument("--suite", choices=["auth", "shop", "e2e"], help="запустить выбранную группу")
    parser.add_argument("--no-open", action="store_true", help="не открывать Allure по завершении")
    parser.add_argument("--phone-demo", action="store_true", help="показать отказ во входе по телефону")
    args = parser.parse_args()

    if settings.browser not in {"chromium", "firefox", "webkit"}:
        parser.error("BROWSER должен быть chromium, firefox или webkit.")
    browser_name = "chromium" if args.phone_demo else settings.browser
    subprocess.run(
        [sys.executable, "-m", "playwright", "install", browser_name],
        cwd=ROOT_DIR,
        check=True,
    )
    if args.phone_demo:
        from core.phone_demo import run_phone_demo

        return run_phone_demo()

    java = prepare_allure()
    environment = {**os.environ, "PYTHONUTF8": "1"}
    if args.headed:
        environment.update(HEADLESS="false", IMODERN_SHOW_STEPS="1")
    selection = ["-m", args.suite] if args.suite else []
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest", "--junitxml=test-results/pytest.xml",
            f"--log-cli-level={settings.log_level}", *selection,
        ],
        cwd=ROOT_DIR,
        env=environment,
    )
    publish_results(
        ROOT_DIR / "allure-results",
        ROOT_DIR / "test-results" / "summary.md",
        settings.private_values,
    )
    report_code = generate_report(java)
    if report_code == 0 and not args.no_open:
        webbrowser.open((ROOT_DIR / "allure-report" / "index.html").as_uri())
    return result.returncode or report_code


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"Run setup failed: {error}", file=sys.stderr)
        raise SystemExit(1)
