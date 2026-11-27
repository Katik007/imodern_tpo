"""Фиксированная версия Allure для автономного HTML-отчёта."""

import os
from pathlib import Path
import shutil
import subprocess
from urllib.request import urlopen
from zipfile import ZipFile

from core.config import ROOT_DIR

VERSION = "2.34.1"
RUNTIME = ROOT_DIR / ".test-runtime"
ALLURE = RUNTIME / f"allure-{VERSION}"


def prepare_allure() -> str:
    java_home = os.getenv("JAVA_HOME")
    java = str(Path(java_home) / "bin" / "java.exe") if java_home else shutil.which("java")
    if not java or not Path(java).is_file():
        raise RuntimeError("Для Allure нужен Java 8+ в PATH или корректный JAVA_HOME.")
    if not (ALLURE / "bin" / "allure.bat").is_file():
        cache = RUNTIME / "downloads"
        cache.mkdir(parents=True, exist_ok=True)
        archive = cache / f"allure-commandline-{VERSION}.zip"
        if not archive.is_file():
            pending = archive.with_suffix(".partial")
            url = (
                "https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/"
                f"{VERSION}/{archive.name}"
            )
            with urlopen(url, timeout=90) as source, pending.open("wb") as target:
                shutil.copyfileobj(source, target)
            pending.replace(archive)
        with ZipFile(archive) as bundle:
            bundle.extractall(RUNTIME)
    return java


def generate_report(java: str) -> int:
    classpath = os.pathsep.join(
        str(path.relative_to(ROOT_DIR)) for path in (ALLURE / "lib" / "*", ALLURE / "lib" / "config")
    )
    result = subprocess.run(
        [
            java, "-cp", classpath, "io.qameta.allure.CommandLine",
            "generate", "--clean", "--single-file", "-o", "allure-report", "allure-results",
        ],
        cwd=ROOT_DIR,
    )
    return result.returncode
