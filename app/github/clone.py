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

from git import Repo
import os
import uuid
from datetime import datetime, timedelta
import shutil

from app.security.url_validator import validate_repository_url


TEMP_FOLDER = "temp"
TEMP_FOLDER_MAX_AGE_HOURS = 72


def cleanup_temp_folders(hours: int = TEMP_FOLDER_MAX_AGE_HOURS):
    os.makedirs(TEMP_FOLDER, exist_ok=True)

    limite = datetime.now() - timedelta(hours=hours)

    for folder in os.listdir(TEMP_FOLDER):
        folder_path = os.path.join(TEMP_FOLDER, folder)

        if not os.path.isdir(folder_path):
            continue

        try:
            data_modificacao = datetime.fromtimestamp(
                os.path.getmtime(folder_path)
            )

            if data_modificacao < limite:
                shutil.rmtree(folder_path)
                print(f"Temporário antigo removido: {folder_path}")

        except FileNotFoundError:
            # Outro processo pode ter removido a pasta ao mesmo tempo.
            continue

        except PermissionError:
            print(f"Temporário em uso, ignorando: {folder_path}")

        except Exception as error:
            print(f"Erro ao remover temporário {folder_path}: {error}")


def clone_repository(repo_url: str):
    repo_url = validate_repository_url(repo_url)

    os.makedirs(TEMP_FOLDER, exist_ok=True)

    # Remove temporários abandonados há mais de 72 horas.
    cleanup_temp_folders(hours=TEMP_FOLDER_MAX_AGE_HOURS)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    repo_id = f"{uuid.uuid4()}_{timestamp}"

    local_path = os.path.join(TEMP_FOLDER, repo_id)

    Repo.clone_from(repo_url, local_path)

    return local_path