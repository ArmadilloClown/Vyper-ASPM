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

from celery import Celery

from app.config import REDIS_URL


celery_app = Celery(
    "vyper",
    include=[
        "app.tasks.scan_task",
        "app.tasks.scheduled_scan_task",
    ]
)

celery_app.conf.update(
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,

    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    timezone="UTC",
    enable_utc=True,

    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,

    beat_schedule={
        "process-scheduled-scans-every-minute": {
            "task": "app.tasks.scheduled_scan_task.process_scheduled_scans",
            "schedule": 60.0,
        },
    },
)