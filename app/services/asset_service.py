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
from app.models.asset import Asset


def save_assets_db(
    scan_id: int,
    asset_type: str,
    assets: list
):

    db = SessionLocal()

    try:

        for asset in assets:

            db_asset = Asset(
                scan_id=scan_id,
                asset_type=asset_type,
                value=str(asset)
            )

            db.add(db_asset)

        db.commit()

        print(
            f"{len(assets)} assets do tipo {asset_type} salvos"
        )

    finally:
        db.close()