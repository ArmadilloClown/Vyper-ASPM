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

def create_fixed_findings(
    fixed_keys
):

    fixed_findings = []

    for key in fixed_keys:

        parts = key.split("|")

        fixed_findings.append({

            "source": parts[0],

            "type": parts[1],

            "file": parts[2],

            "severity": "INFO",

            "title": "Finding Fixed",

            "description":
                "This finding was fixed in the latest scan.",

            "status": "fixed",

            "risk_score": 0
        })

    return fixed_findings