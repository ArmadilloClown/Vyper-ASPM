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

import json
import redis
from app.config import REDIS_URL


redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True
)


def send_progress(
    task_id,
    progress,
    message
):

    data = {
        "progress": progress,
        "message": message
    }

    try:

        redis_client.set(
            f"scan_progress:{task_id}",
            json.dumps(data),
            ex=3600
        )

        redis_client.publish(
            f"scan_progress:{task_id}",
            json.dumps(data)
        )

    except Exception as error:

        print(
            "ERRO AO PUBLICAR PROGRESSO:",
            repr(error)
        )