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

from app.utils.risk_score import calculate_risk_score

def normalize_semgrep(raw_findings):

    normalized = []

    results = raw_findings.get(
        "results",
        []
    )

    for finding in results:

        metadata = finding.get(
            "extra",
            {}
        ).get(
            "metadata",
            {}
        )

        normalized.append({

            "source": "semgrep",

            "type": finding.get(
                "check_id"
            ),

            "severity": finding.get(
                "extra",
                {}
            ).get(
                "severity"
            ),

            "file": finding.get(
                "path"
            ),

            "line": finding.get(
                "start",
                {}
            ).get(
                "line"
            ),

            "title": finding.get(
                "check_id"
            ),

            "description": finding.get(
                "extra",
                {}
            ).get(
                "message"
            ),

            "rule_id": finding.get(
                "check_id"
            ),

            "category": metadata.get(
                "category"
            ),

            "owasp": str(
                metadata.get(
                    "owasp",
                    []
                )
            ),

            "cwe": str(
                metadata.get(
                    "cwe",
                    []
                )
            ),

            "risk_score": 10,

            "status": "new"
        })

    return normalized