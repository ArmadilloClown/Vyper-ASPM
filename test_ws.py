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
import websockets


async def main():
    print("Conectando ao WebSocket...")

    websocket = await websockets.connect(
        "ws://127.0.0.1:8000/ws/teste"
    )

    print("WEBSOCKET CONECTADO!")
    print("Aguardando mensagem do Redis...")
    print(">>> Agora abra OUTRO terminal e publique a mensagem.")
    print(">>> Pressione Ctrl+C para encerrar.")

    try:
        while True:
            mensagem = await websocket.recv()

            print("\n==============================")
            print("MENSAGEM RECEBIDA:")
            print(mensagem)
            print("==============================\n")

    except websockets.exceptions.ConnectionClosed:
        print("WebSocket foi fechado pelo servidor.")

    except KeyboardInterrupt:
        print("Teste encerrado.")

    finally:
        await websocket.close()


asyncio.run(main())