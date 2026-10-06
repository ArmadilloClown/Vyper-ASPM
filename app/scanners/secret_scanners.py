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
import os
import shutil
import subprocess


GITLEAKS_BIN = os.getenv("GITLEAKS_BIN") or shutil.which("gitleaks")


def scan_secrets(repo_path):
    if not GITLEAKS_BIN:
        raise RuntimeError("Gitleaks não encontrado no ambiente.")

    command = [
        GITLEAKS_BIN,
        "detect",
        "--source",
        repo_path,
        "--report-format",
        "json",
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=600,
    )

    if not result.stdout.strip():
        return []

    try:
        findings = json.loads(result.stdout)
        return findings

    except json.JSONDecodeError:
        return []