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

from app.celery_app import celery_app
from app.database.session import SessionLocal
from app.models.scheduled_scan import ScheduledScan
from app.tasks.scan_task import scan_repository


@celery_app.task
def process_scheduled_scans():
    db = SessionLocal()

    try:
        now = datetime.utcnow()

        scheduled_scans = (
            db.query(ScheduledScan)
            .filter(
                ScheduledScan.enabled == True,
                (
                    ScheduledScan.next_run_at.is_(None)
                    | (ScheduledScan.next_run_at <= now)
                ),
            )
            .all()
        )

        dispatched = 0

        for scheduled_scan in scheduled_scans:

            # Segurança adicional:
            # nunca iniciar um novo scan enquanto o anterior
            # ainda estiver marcado como iniciado e não finalizado.
            if (
                scheduled_scan.last_started_at is not None
                and (
                    scheduled_scan.last_finished_at is None
                    or scheduled_scan.last_finished_at
                    < scheduled_scan.last_started_at
                )
            ):
                continue

            # Primeiro agendamento:
            # pode executar imediatamente.
            #
            # Agendamentos seguintes:
            # precisam respeitar o intervalo contado
            # a partir do término do último scan.
            if scheduled_scan.last_finished_at is not None:

                next_allowed_run = (
                    scheduled_scan.last_finished_at
                    + timedelta(
                        minutes=scheduled_scan.interval_minutes
                    )
                )

                if now < next_allowed_run:
                    scheduled_scan.next_run_at = next_allowed_run
                    continue

            scheduled_scan.last_started_at = now

            scheduled_scan.next_run_at = (
                now
                + timedelta(
                    minutes=scheduled_scan.interval_minutes
                )
            )

            db.commit()

            scan_repository.delay(
                scheduled_scan.repository_url,
                scheduled_scan.id,
            )

            dispatched += 1

        return {
            "checked": len(scheduled_scans),
            "dispatched": dispatched,
        }

    finally:
        db.close()