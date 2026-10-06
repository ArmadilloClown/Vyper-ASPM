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


def save_findings_db(scan_id, findings):

    db = SessionLocal()

    try:

        for finding in findings:

            db_finding = Finding(
                scan_id=scan_id,
                source=finding.get("source"),
                severity=finding.get("severity"),
                type=finding.get("type"),
                title=finding.get("title"),
                description=finding.get("description"),
                file=finding.get("file"),
                line=finding.get("line"),

                package_name=finding.get(
                    "package_name"
                ),

                installed_version=finding.get(
                    "installed_version"
                ),

                fixed_version=finding.get(
                    "fixed_version"
                ),

                risk_score=finding.get(
                    "risk_score"
                ),

                status=finding.get(
                    "status"
                ),

                risk_id=finding.get(
                    "risk_id"
                ),

                cve=finding.get(
                    "cve"
                ),

                cvss=finding.get(
                    "cvss"
                ),

                rule_id=finding.get(
                    "rule_id"
                ),

                category=finding.get(
                    "category"
                ),

                owasp=finding.get(
                    "owasp"
                ),

                cwe=finding.get(
                    "cwe"
                )
            )

            print(
                "SALVANDO:",
                db_finding.title,
                db_finding.cvss
            )

            db.add(db_finding)

        db.commit()

        print(f"{len(findings)} findings salvos no banco")

    finally:
        db.close()