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

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import ForeignKey

from app.database.base import Base


class Finding(Base):
    __tablename__ = "findings"

    id = Column(
        Integer,
        primary_key=True
    )

    scan_id = Column(
        Integer,
        ForeignKey("scans.id")
    )

    risk_id = Column(
    Integer,
    ForeignKey("risks.id")
    )

    source = Column(String)

    severity = Column(String)

    type = Column(String)

    title = Column(String)

    description = Column(Text)

    file = Column(String)

    line = Column(Integer)

    package_name = Column(String)

    installed_version = Column(String)

    fixed_version = Column(String)

    risk_score = Column(Integer)

    status = Column(String)

    cve = Column(String)

    cvss = Column(String)

    rule_id = Column(String)

    category = Column(String)

    owasp = Column(Text)

    cwe = Column(Text)