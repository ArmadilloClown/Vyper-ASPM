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
import os


def get_previous_scan(
    repository_url: str,
    current_scan_id: int
):
    db = SessionLocal()

    try:
        previous_scan = (
            db.query(Scan)
            .filter(
                Scan.repository_url == repository_url,
                Scan.id < current_scan_id
            )
            .order_by(
                Scan.id.desc()
            )
            .first()
        )

        return previous_scan

    finally:
        db.close()


def get_findings_from_scan(
    scan_id: int
):
    db = SessionLocal()

    try:
        findings = (
            db.query(Finding)
            .filter(
                Finding.scan_id == scan_id
            )
            .all()
        )

        print(
            f"SCAN {scan_id} TEM {len(findings)} FINDINGS"
        )

        return findings

    finally:
        db.close()


def normalize_file_path(path):

    if not path:
        return ""

    path = path.replace("\\", "/")

    if "vulnerabilities/" in path:
        return path.split("vulnerabilities/")[1]

    return os.path.basename(path)


def generate_finding_key(finding):

    if isinstance(finding, dict):

        file_path = normalize_file_path(
            finding.get("file")
        )

        return (
            f"{finding.get('source')}|"
            f"{finding.get('type')}|"
            f"{file_path}"
        )

    file_path = normalize_file_path(
        finding.file
    )

    return (
        f"{finding.source}|"
        f"{finding.type}|"
        f"{file_path}"
    )


def compare_findings(
    previous_findings,
    current_findings
):

    previous_keys = {
        generate_finding_key(f)
        for f in previous_findings
    }

    current_keys = set()

    for finding in current_findings:

        key = generate_finding_key(
            finding
        )

        current_keys.add(key)

        if key in previous_keys:
            finding["status"] = "active"

        else:
            finding["status"] = "new"

    fixed_keys = previous_keys - current_keys

    return fixed_keys