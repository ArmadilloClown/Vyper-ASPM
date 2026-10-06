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
from app.models.scan import Scan


def compare_scan(scan_id: int):

    db = SessionLocal()

    try:

        # -----------------------------------------
        # Scan atual
        # -----------------------------------------

        current_scan = (
            db.query(Scan)
            .filter(Scan.id == scan_id)
            .first()
        )

        if not current_scan:
            raise ValueError(
                f"Scan {scan_id} não encontrado."
            )

        current_findings = (
            db.query(Finding)
            .filter(Finding.scan_id == scan_id)
            .all()
        )

        # -----------------------------------------
        # Scan anterior do MESMO repositório
        # -----------------------------------------

        previous_scan = (
            db.query(Scan)
            .filter(
                Scan.repository_url == current_scan.repository_url,
                Scan.id < scan_id,
                Scan.status == "completed"
            )
            .order_by(Scan.id.desc())
            .first()
        )

        # Não existe scan anterior
        if not previous_scan:

            return {
                "current_scan": scan_id,
                "previous_scan": None,
                "new_findings": len(current_findings),
                "fixed_findings": 0,
                "unchanged_findings": 0
            }

        previous_findings = (
            db.query(Finding)
            .filter(
                Finding.scan_id == previous_scan.id
            )
            .all()
        )

        # -----------------------------------------
        # Identidade do finding
        # -----------------------------------------

        current_set = {
            (
                f.source,
                f.type,
                f.file
            )
            for f in current_findings
        }

        previous_set = {
            (
                f.source,
                f.type,
                f.file
            )
            for f in previous_findings
        }

        # -----------------------------------------
        # Comparação
        # -----------------------------------------

        new_findings = (
            current_set - previous_set
        )

        fixed_findings = (
            previous_set - current_set
        )

        unchanged_findings = (
            current_set & previous_set
        )

        return {
            "current_scan": scan_id,
            "previous_scan": previous_scan.id,
            "new_findings": len(new_findings),
            "fixed_findings": len(fixed_findings),
            "unchanged_findings": len(
                unchanged_findings
            )
        }

    finally:
        db.close()