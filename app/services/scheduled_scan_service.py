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

from datetime import datetime, timedelta

from app.database.session import SessionLocal
from app.models.scheduled_scan import ScheduledScan


MIN_INTERVAL_MINUTES = 10


def create_scheduled_scan(
    repository_url: str,
    interval_minutes: int
):
    if interval_minutes < MIN_INTERVAL_MINUTES:
        raise ValueError(
            "O intervalo mínimo é de 10 minutos."
        )

    db = SessionLocal()

    try:
        existing = (
            db.query(ScheduledScan)
            .filter(
                ScheduledScan.repository_url == repository_url
            )
            .first()
        )

        if existing:
            raise ValueError(
                "Já existe um agendamento para este repositório."
            )

        scheduled_scan = ScheduledScan(
            repository_url=repository_url,
            enabled=True,
            interval_minutes=interval_minutes
        )

        db.add(scheduled_scan)
        db.commit()
        db.refresh(scheduled_scan)

        return scheduled_scan

    finally:
        db.close()


def get_scheduled_scans():
    db = SessionLocal()

    try:
        return (
            db.query(ScheduledScan)
            .order_by(ScheduledScan.id.desc())
            .all()
        )

    finally:
        db.close()


def get_scheduled_scan(scheduled_scan_id: int):
    db = SessionLocal()

    try:
        return (
            db.query(ScheduledScan)
            .filter(
                ScheduledScan.id == scheduled_scan_id
            )
            .first()
        )

    finally:
        db.close()


def update_scheduled_scan(
    scheduled_scan_id: int,
    interval_minutes: int | None = None,
    enabled: bool | None = None
):
    if (
        interval_minutes is not None
        and interval_minutes < MIN_INTERVAL_MINUTES
    ):
        raise ValueError(
            "O intervalo mínimo é de 10 minutos."
        )

    db = SessionLocal()

    try:
        scheduled_scan = (
            db.query(ScheduledScan)
            .filter(
                ScheduledScan.id == scheduled_scan_id
            )
            .first()
        )

        if not scheduled_scan:
            return None

        if interval_minutes is not None:
            scheduled_scan.interval_minutes = interval_minutes

        if enabled is not None:
            scheduled_scan.enabled = enabled

        scheduled_scan.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(scheduled_scan)

        return scheduled_scan

    finally:
        db.close()


def delete_scheduled_scan(scheduled_scan_id: int):
    db = SessionLocal()

    try:
        scheduled_scan = (
            db.query(ScheduledScan)
            .filter(
                ScheduledScan.id == scheduled_scan_id
            )
            .first()
        )

        if not scheduled_scan:
            return False

        db.delete(scheduled_scan)
        db.commit()

        return True

    finally:
        db.close()