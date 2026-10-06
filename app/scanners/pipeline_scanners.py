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

import os 

def scan_pipelines(repo_path):
    pipelines= []

    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if ".github/workflows" in root:
                pipelines.append({
                    "type": "github_actions",
                    "file": file
                })

            if file == ".githublab-ci.yml":
                pipelines.append({
                    "type": "github_pipeline",
                    "file": file
                })

    return pipelines