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
import shutil
import subprocess
import json


def run_semgrep(path: str):
    """
    Executa o Semgrep no diretório informado e retorna o JSON bruto.
    """

    # Permite configurar manualmente pelo .env/sistema.
    # Caso não exista, procura o executável no PATH.
    semgrep_bin = os.getenv("SEMGREP_BIN") or shutil.which("semgrep")

    if not semgrep_bin:
        raise RuntimeError(
            "Semgrep não encontrado. "
            "Verifique se está instalado e disponível no PATH."
        )

    command = [
        semgrep_bin,
        "scan",
        "--config=auto",
        "--exclude",
        ".next",
        "--exclude",
        "node_modules",
        "--exclude",
        "venv",
        "--exclude",
        "__pycache__",
        "--exclude",
        ".git",
        path,
        "--json",
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
        )

    except subprocess.TimeoutExpired as e:
        raise RuntimeError(
            "Semgrep excedeu o tempo máximo de execução (10 minutos)."
        ) from e

    except FileNotFoundError as e:
        raise RuntimeError(
            f"Executável do Semgrep não encontrado: {semgrep_bin}"
        ) from e

    if result.returncode != 0:
        raise RuntimeError(
            "Semgrep falhou.\n"
            f"Return code: {result.returncode}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            "Semgrep retornou uma saída que não é JSON válido."
        ) from e