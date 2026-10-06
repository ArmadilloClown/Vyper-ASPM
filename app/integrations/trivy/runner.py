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

import json
import shutil
import subprocess


TRIVY_TIMEOUT = 600


def run_trivy(repo_path: str):
    """
    Executa o Trivy no diretório do repositório
    e retorna o JSON bruto.
    """

    trivy_bin = shutil.which("trivy")

    if not trivy_bin:
        raise RuntimeError(
            "Trivy não encontrado. "
            "Verifique se está instalado e disponível no PATH."
        )

    command = [
        trivy_bin,
        "fs",
        "--format",
        "json",
        repo_path,
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TRIVY_TIMEOUT,
        )

    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            "Trivy excedeu o tempo máximo de execução "
            f"({TRIVY_TIMEOUT // 60} minutos)."
        ) from exc

    except FileNotFoundError as exc:
        raise RuntimeError(
            f"Executável do Trivy não encontrado: {trivy_bin}"
        ) from exc

    if result.returncode != 0:
        raise RuntimeError(
            "Trivy falhou.\n"
            f"Return code: {result.returncode}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )

    try:
        return json.loads(result.stdout)

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Trivy retornou uma saída que não é JSON válido."
        ) from exc