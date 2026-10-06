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

from app.services.risk_score_service import calculate_risk_score

def normalize_zap(raw_alerts):

    normalized = []

    for alert in raw_alerts:

        normalized.append({

            "source": "zap",

            "type": alert.get(
                "pluginId",
                "unknown"
            ),

            "severity": alert.get(
                "risk",
                "Info"
            ),

            "title": alert.get(
                "alert",
                ""
            ),

            "description": alert.get(
                "description",
                ""
            ),

            "file": alert.get(
                "url",
                ""
            ),

            "line": None,

            "package_name": None,

            "installed_version": None,

            "fixed_version": None,

            "cvss": None,

            "risk_score": calculate_risk_score(
                severity=alert.get("risk","").upper(),
                evidence_count=1
            ),

            "status": "new"
        })

    return normalized