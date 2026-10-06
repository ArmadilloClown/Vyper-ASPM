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

import asyncio
import json
import redis

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websocket.manager import manager
from app.config import REDIS_URL


router = APIRouter()

redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True
)


def parse_progress(value):
    """
    Converte um payload Redis em dict.
    Retorna None caso o conteúdo não seja JSON válido.
    """

    if not value:
        return None

    try:
        data = json.loads(value)

        if not isinstance(data, dict):
            return None

        return data

    except (json.JSONDecodeError, TypeError):
        print(
            "AVISO: payload inválido recebido no Redis:",
            repr(value)
        )
        return None


@router.websocket("/ws/{task_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    task_id: str
):

    await manager.connect(
        task_id,
        websocket
    )

    pubsub = redis_client.pubsub()

    channel = f"scan_progress:{task_id}"

    try:

        pubsub.subscribe(channel)

        # Envia o último progresso conhecido,
        # caso o scan tenha começado antes da conexão.
        last_progress = redis_client.get(channel)

        data = parse_progress(last_progress)

        if data is not None:

            await websocket.send_json(
                data
            )

        while True:

            message = pubsub.get_message(
                ignore_subscribe_messages=True
            )

            if message:

                data = parse_progress(
                    message.get("data")
                )

                if data is None:
                    await asyncio.sleep(0.2)
                    continue

                await websocket.send_json(
                    data
                )

                if data.get("progress") == 100:
                    break

            await asyncio.sleep(0.2)

    except WebSocketDisconnect:

        print(
            f"WebSocket desconectado: {task_id}"
        )

    except Exception as error:

        print(
            "ERRO NO WEBSOCKET:",
            repr(error)
        )

    finally:

        try:
            pubsub.close()
        except Exception:
            pass

        manager.disconnect(
            task_id
        )