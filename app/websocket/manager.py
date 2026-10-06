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

from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):

        self.connections = {}

    async def connect(

        self,

        task_id,

        websocket: WebSocket

    ):

        await websocket.accept()

        self.connections[task_id] = websocket

    def disconnect(

        self,

        task_id

    ):

        if task_id in self.connections:

            del self.connections[task_id]

    async def send(

        self,

        task_id,

        data

    ):

        websocket = self.connections.get(task_id)

        if websocket:

            await websocket.send_json(data)


manager = ConnectionManager()