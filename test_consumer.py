from __future__ import annotations

import unittest

from websockets.asyncio.server import serve

from consumer import consume_feed
from mock_feed import replay_messages


EXPECTED_RESULT = {
    "event_id": "fight-101",
    "totals": {
        "red": {"knockdowns": 0, "total_strikes_landed": 16},
        "blue": {"knockdowns": 2, "total_strikes_landed": 13},
    },
}


class FeedIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_feed_returns_correct_totals(self) -> None:
        async with serve(replay_messages, "127.0.0.1", 0) as server:
            port = server.sockets[0].getsockname()[1]
            result = await consume_feed(f"ws://127.0.0.1:{port}/feed")

        self.assertEqual(result, EXPECTED_RESULT)


if __name__ == "__main__":
    unittest.main()
