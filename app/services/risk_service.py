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
from app.services.risk_score_service import (
    calculate_risk_score,
    get_highest_cvss,
    risk_has_cve,
    risk_has_fix,
    get_risk_priority
)


def find_or_create_risk(
    title,
    severity,
    evidence_count,
    status,
    score,
    priority
):

    db = SessionLocal()

    try:

        risk = (
            db.query(Risk)
            .filter(
                Risk.title == title
            )
            .first()
        )

        if risk:

            risk.evidence_count = evidence_count

            risk.severity = severity

            risk.status = status

            risk.score = score

            risk.priority = priority

            db.commit()

            return risk.id

        risk = Risk(
            title=title,
            severity=severity,
            score=score,
            priority=priority,
            status=status,
            evidence_count=evidence_count
        )

        db.add(risk)

        db.commit()

        db.refresh(risk)

        return risk.id

    finally:
        db.close()

def get_risk_title(finding):

    cwe = finding.get("cwe")

    if cwe:

        if "CWE-78" in cwe:
            return "Command Injection"

        if "CWE-89" in cwe:
            return "SQL Injection"

        if "CWE-79" in cwe:
            return "Cross-Site Scripting"

        if "CWE-22" in cwe:
            return "Path Traversal"

        return cwe

    if finding.get("cve"):

        return finding.get("title")

    if finding.get("category"):

        return finding.get("category")

    return finding.get("type")

def correlate_findings(findings):

    grouped = {}

    for finding in findings:

        risk_title = get_risk_title(
            finding
        )

        if risk_title not in grouped:
            grouped[risk_title] = []

        grouped[risk_title].append(
            finding
        )

    for risk_title, risk_findings in grouped.items():

        severity = get_highest_severity(
            risk_findings
        )

        evidence_count = len(
            risk_findings
        )

        highest_cvss = get_highest_cvss(
            risk_findings
        )

        has_cve = risk_has_cve(
            risk_findings
        )

        has_fix = risk_has_fix(
            risk_findings
        )

        score = calculate_risk_score(
            severity=severity,
            evidence_count=evidence_count,
            cvss=highest_cvss,
            has_cve=has_cve,
            has_fix=has_fix
        )

        priority = get_risk_priority(
            score
        )

        
        risk_status= get_risk_status(
            risk_findings
        )

        print(
            "RISK:",
            risk_title,
            "EVIDENCE:",
            evidence_count
        )

        risk_id = find_or_create_risk(
            title=risk_title,
            severity=severity,
            evidence_count=evidence_count,
            status= risk_status,
            score=score,
            priority=priority
        )

        for finding in risk_findings:

            finding["risk_id"] = risk_id

    return findings

def get_highest_severity(findings):

    severity_order = {
        "INFO": 1,
        "LOW": 2,
        "WARNING": 3,
        "MEDIUM": 4,
        "HIGH": 5,
        "CRITICAL": 6,
        "ERROR": 7
    }

    highest = "INFO"

    for finding in findings:

        severity = finding.get(
            "severity",
            "INFO"
        )

        if severity_order.get(
            severity,
            0
        ) > severity_order.get(
            highest,
            0
        ):
            highest = severity

    return highest

def get_risk_status(findings):

    for finding in findings:
        if finding.get("status") != "fixed":
            return "active"
        
    return "fixed"