from __future__ import annotations

import asyncio
import json
from collections.abc import Iterable
from typing import Any

from websockets.asyncio.server import ServerConnection, serve


HOST = "127.0.0.1"
PORT = 8765

MESSAGES: tuple[dict[str, Any], ...] = (
    {
        "seq": 1,
        "event_id": "fight-101",
        "action": "start_round",
        "data": {"round": 1},
    },
    {
        "seq": 2,
        "event_id": "fight-101",
        "action": "stats",
        "data": {
            "round": 1,
            "elapsed_seconds": 180,
            "competitor": "red",
            "knockdowns": 0,
            "total_strikes_landed": 12,
        },
    },
    {
        "seq": 3,
        "event_id": "fight-101",
        "action": "stats",
        "data": {
            "round": 1,
            "elapsed_seconds": 180,
            "competitor": "blue",
            "knockdowns": 1,
            "total_strikes_landed": 9,
        },
    },
    {
        "seq": 4,
        "event_id": "fight-101",
        "action": "round_end",
        "data": {"round": 1},
    },
    {
        "seq": 5,
        "event_id": "fight-101",
        "action": "stats",
        "data": {
            "round": 1,
            "elapsed_seconds": 180,
            "competitor": "blue",
            "knockdowns": 2,
            "total_strikes_landed": 10,
        },
    },
    {
        "seq": 6,
        "event_id": "fight-101",
        "action": "start_round",
        "data": {"round": 2},
    },
    {
        "seq": 7,
        "event_id": "fight-101",
        "action": "stats",
        "data": {
            "round": 2,
            "elapsed_seconds": 30,
            "competitor": "red",
            "knockdowns": 0,
            "total_strikes_landed": 4,
        },
    },
    {
        "seq": 8,
        "event_id": "fight-101",
        "action": "stats",
        "data": {
            "round": 2,
            "elapsed_seconds": 30,
            "competitor": "blue",
            "knockdowns": 0,
            "total_strikes_landed": 3,
        },
    },
    {
        "seq": 8,
        "event_id": "fight-101",
        "action": "stats",
        "data": {
            "round": 2,
            "elapsed_seconds": 30,
            "competitor": "blue",
            "knockdowns": 0,
            "total_strikes_landed": 3,
        },
    },
    {
        "seq": 9,
        "event_id": "fight-101",
        "action": "end_fight",
        "data": {},
    },
)


async def replay_messages(
    websocket: ServerConnection,
    messages: Iterable[dict[str, Any]] = MESSAGES,
) -> None:
    if websocket.request is not None and websocket.request.path != "/feed":
        await websocket.close(code=1008, reason="use /feed")
        return

    for message in messages:
        await websocket.send(json.dumps(message))
        await asyncio.sleep(0.01)


async def run_server() -> None:
    async with serve(replay_messages, HOST, PORT) as server:
        print(f"Mock feed listening at ws://{HOST}:{PORT}/feed")
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        pass
