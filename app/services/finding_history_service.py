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
from app.models.finding import Finding


def get_findings_by_scan(scan_id: int):

    db = SessionLocal()

    try:

        findings = (
            db.query(Finding)
            .filter(Finding.scan_id == scan_id)
            .all()
        )

        result = []

        for finding in findings:

            result.append({
                "id": finding.id,
                "source": finding.source,
                "severity": finding.severity,
                "type": finding.type,
                "title": finding.title,
                "description": finding.description,
                "file": finding.file,
                "line": finding.line
            })

        return result

    finally:
        db.close()