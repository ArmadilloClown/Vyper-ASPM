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

from datetime import datetime

from app.database.session import SessionLocal
from app.models.scan import Scan


def create_scan(repo_url: str):

    print("CREATE_SCAN FOI CHAMADO")

    db = SessionLocal()

    try:

        scan = Scan(
            repository_url=repo_url,
            status="running"
        )

        db.add(scan)

        db.commit()

        db.refresh(scan)

        print("SCAN CRIADO:", scan.id)

        return scan.id

    finally:
        db.close()


def update_scan_status(scan_id: int, status: str):

    db = SessionLocal()

    try:

        scan = db.query(Scan).filter(
            Scan.id == scan_id
        ).first()

        if scan:

            scan.status = status

            if status in [
                "completed",
                "failed"
            ]:

                scan.finished_at = datetime.utcnow()

            db.commit()

            print(
                f"SCAN {scan_id} atualizado para {status}"
            )

    finally:
        db.close()