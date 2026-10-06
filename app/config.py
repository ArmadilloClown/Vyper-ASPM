# Vyper ASPM
#
# Copyright (C) 2026 Pedro
#
# This file is part of Vyper ASPM.
#
# Vyper ASPM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Vyper ASPM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Vyper ASPM. If not, see <https://www.gnu.org/licenses/>.

import os

from dotenv import load_dotenv


load_dotenv()


def get_env(name: str, default=None, required: bool = False):
    value = os.getenv(name, default)

    if required and not value:
        raise RuntimeError(
            f"Variável de ambiente obrigatória não configurada: {name}"
        )

    return value


DATABASE_URL = get_env(
    "DATABASE_URL",
    required=True
)

REDIS_URL = get_env(
    "REDIS_URL",
    "redis://localhost:6379/0"
)

CORS_ORIGINS = [
    origin.strip()
    for origin in get_env(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if origin.strip()
]

OLLAMA_URL = get_env(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)

OLLAMA_MODEL = get_env(
    "OLLAMA_MODEL",
    "llama3.2"
)

AI_TIMEOUT = int(
    get_env("AI_TIMEOUT", "120")
)

AI_TEMPERATURE = float(
    get_env("AI_TEMPERATURE", "0.2")
)

ZAP_URL = get_env(
    "ZAP_URL",
    "http://127.0.0.1:8080"
)

ZAP_API_KEY = get_env(
    "ZAP_API_KEY"
)

ZAP_VERIFY_SSL = (
    get_env("ZAP_VERIFY_SSL", "true").lower() == "true"
)

ZAP_TIMEOUT = int(
    get_env("ZAP_TIMEOUT", "30")
)

ZAP_SCAN_TIMEOUT = int(
    get_env("ZAP_SCAN_TIMEOUT", "900")
)

ZAP_TARGET_URL = get_env(
    "ZAP_TARGET_URL"
)

SEMGREP_BIN = get_env(
    "SEMGREP_BIN"
)

TRIVY_BIN = get_env(
    "TRIVY_BIN"
)

GITLEAKS_BIN = get_env(
    "GITLEAKS_BIN"
)
