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

def calculate_risk_score(
    severity,
    evidence_count,
    cvss=None,
    has_cve=False,
    has_fix=False
):

    score = 0

    severity_scores = {
        "INFO": 5,
        "INFORMATIONAL": 5,
        "LOW": 10,
        "WARNING": 20,
        "MEDIUM": 30,
        "HIGH": 50,
        "CRITICAL": 70,
        "ERROR": 80
    }

    score += severity_scores.get(
        severity,
        0
    )

    if cvss:

        if cvss >= 9:
            score += 20

        elif cvss >= 7:
            score += 10

    if evidence_count > 5:
        score += 10

    return score

def get_highest_cvss(findings):

    highest = 0

    for finding in findings:

        cvss = finding.get("cvss")

        if cvss is None:
            continue

        try:

            cvss = float(cvss)

            if cvss > highest:
                highest = cvss

        except:

            pass

    return highest

def risk_has_cve(findings):

    for finding in findings:

        if finding.get("cve"):
            return True

    return False

def risk_has_fix(findings):

    for finding in findings:

        if finding.get("fixed_version"):
            return True

    return False

def get_risk_priority(score):

    if score >= 90:
        return "Critical"

    if score >= 70:
        return "High"

    if score >= 40:
        return "Medium"

    return "Low"