from __future__ import annotations

import argparse
import asyncio
import json
from typing import Any

from websockets.asyncio.client import connect


STAT_FIELDS = ("knockdowns", "total_strikes_landed")
COMPETITORS = ("red", "blue")


class StatsProcessor:
    def __init__(self) -> None:
        self.event_id: str | None = None
        self.totals = {
            competitor: {field: 0 for field in STAT_FIELDS}
            for competitor in COMPETITORS
        }

    def apply(self, message: dict[str, Any]) -> None:
        if self.event_id is None and message.get("event_id") is not None:
            self.event_id = str(message["event_id"])

        if message.get("action") != "stats":
            return

        data = message.get("data") or {}
        competitor = data.get("competitor")
        if competitor not in self.totals:
            return

        # BUG: stats are cumulative round snapshots, not increments.
        for field in STAT_FIELDS:
            self.totals[competitor][field] += int(data.get(field, 0))

    def result(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "totals": {
                competitor: dict(values)
                for competitor, values in self.totals.items()
            },
        }


async def consume_feed(url: str) -> dict[str, Any]:
    processor = StatsProcessor()

    async with connect(url) as websocket:
        async for raw_message in websocket:
            message = json.loads(raw_message)
            processor.apply(message)

            # TODO: stop processing when the logical event has ended.

    return processor.result()


def main() -> None:
    parser = argparse.ArgumentParser(description="Consume the interview mock feed")
    parser.add_argument(
        "url",
        nargs="?",
        default="ws://127.0.0.1:8765/feed",
        help="WebSocket feed URL",
    )
    args = parser.parse_args()
    print(json.dumps(asyncio.run(consume_feed(args.url)), indent=2))


if __name__ == "__main__":
    main()
