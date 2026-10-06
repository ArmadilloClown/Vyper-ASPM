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

from app.database.session import SessionLocal
from app.models.scan import Scan


def get_all_scans():

    db = SessionLocal()

    try:

        scans = db.query(Scan).all()

        result = []

        for scan in scans:

            result.append({
                "id": scan.id,
                "repository_url": scan.repository_url,
                "status": scan.status,
                "created_at": scan.created_at,
                "finished_at": scan.finished_at
            })

        return result

    finally:
        db.close()