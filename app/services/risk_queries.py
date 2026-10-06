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
from app.models.risk import Risk
from app.models.finding import Finding


def get_all_risks():

    db = SessionLocal()

    try:

        risks = (
            db.query(Risk)
            .order_by(
                Risk.score.desc()
            )
            .all()
        )

        result = []

        for risk in risks:

            result.append({
                "id": risk.id,
                "title": risk.title,
                "severity": risk.severity,
                "score": risk.score,
                "priority": risk.priority,
                "status": risk.status,
                "evidence_count": risk.evidence_count
            })

        return result

    finally:
        db.close()


def get_risk_by_id(risk_id: int):

    db = SessionLocal()

    try:

        risk = (
            db.query(Risk)
            .filter(Risk.id == risk_id)
            .first()
        )

        if not risk:
            return {"error": "Risk not found"}

        return {
            "id": risk.id,
            "title": risk.title,
            "severity": risk.severity,
            "score": risk.score,
            "priority": risk.priority,
            "status": risk.status,
            "evidence_count": risk.evidence_count
        }

    finally:
        db.close()


def get_findings_by_risk(risk_id: int):

    db = SessionLocal()

    try:

        findings = (
            db.query(Finding)
            .filter(Finding.risk_id == risk_id)
            .all()
        )

        result = []

        for finding in findings:

            result.append({
                "id": finding.id,
                "source": finding.source,
                "severity": finding.severity,
                "title": finding.title,
                "status": finding.status,
                "file": finding.file
            })

        return result

    finally:
        db.close()