"""
WebSocket queue connection manager.
"""

from typing import Dict, List

from fastapi import WebSocket


class QueueConnectionManager:

    def __init__(self):

        self.active_connections: Dict[
            int,
            List[WebSocket]
        ] = {}


    # ========================================================
    # CONNECT
    # ========================================================

    async def connect(
        self,
        centre_id: int,
        websocket: WebSocket
    ):

        await websocket.accept()

        self.active_connections.setdefault(
            centre_id,
            []
        ).append(websocket)


    # ========================================================
    # DISCONNECT
    # ========================================================

    def disconnect(
        self,
        centre_id: int,
        websocket: WebSocket
    ):

        connections = self.active_connections.get(
            centre_id,
            []
        )

        if websocket in connections:

            connections.remove(websocket)

        if not connections:

            self.active_connections.pop(
                centre_id,
                None
            )


    # ========================================================
    # BROADCAST
    # ========================================================

    async def broadcast(
        self,
        centre_id: int,
        data: dict
    ):

        stale_connections = []

        connections = list(
            self.active_connections.get(
                centre_id,
                []
            )
        )

        for connection in connections:

            try:

                await connection.send_json(
                    data
                )

            except Exception:

                stale_connections.append(
                    connection
                )


        for connection in stale_connections:

            self.disconnect(
                centre_id,
                connection
            )


manager = QueueConnectionManager()