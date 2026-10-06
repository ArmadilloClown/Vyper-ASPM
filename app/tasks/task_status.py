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

from celery.result import AsyncResult

from app.celery_app import celery_app


def get_task_status(task_id):

    task = AsyncResult(
        task_id,
        app=celery_app
    )

    response = {

        "task_id": task.id,

        "status": task.status

    }

    if task.state == "PROGRESS":

        response["progress"] = task.info.get(
            "progress"
        )

        response["message"] = task.info.get(
            "message"
        )

    elif task.ready():

        response["result"] = task.result

    return response