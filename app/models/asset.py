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
from sqlalchemy import ForeignKey

from app.database.base import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(
        Integer,
        primary_key=True
    )

    scan_id = Column(
        Integer,
        ForeignKey("scans.id")
    )

    asset_type = Column(String)

    value = Column(String)