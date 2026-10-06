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

def normalize_trivy(raw_findings):

    if not raw_findings:
        return[]

    #print("TRIVY RAW:", raw_findings.keys() if raw_findings else "VAZIO")

    normalized = []

    for result in raw_findings.get("Results", []):

        print("TARGET:", result.get("Target"))

        vulns= result.get("Vulnerabilities", [])

        print("VULNS ENCONTRADAS:", len(vulns))


        for vuln in vulns:

            severity= vuln.get("Severity")

            normalized.append({
                "source": "trivy",
                "type": vuln.get("VulnerabilityID"),
                "severity": severity,
                "file": result.get("Target"),

                "title": vuln.get(
                 "VulnerabilityID"
                ),

                "description": vuln.get(
                "Title"
                ),

                "package_name": vuln.get(
                "PkgName"
                ),

                "installed_version": vuln.get(
                "InstalledVersion"
                ),

                "fixed_version": vuln.get(
                "FixedVersion"
                ),

               "cve": vuln.get(
                    "VulnerabilityID"
                ),

                "cvss": str(
                    vuln.get(
                        "CVSS",
                        {}
                    )
                    .get(
                        "ghsa",
                        {}
                    )
                    .get(
                        "V40Score"
                    )
                ),

                "risk_score": 50,

                "status": "new"
            })

    print("TOTAL NORMALIZADO:", len(normalized))

    return normalized