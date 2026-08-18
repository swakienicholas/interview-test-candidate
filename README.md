# Live Feed Debugging Exercise

## Scenario

A live boxing statistics service is producing incorrect fight totals.

The service receives JSON messages over a WebSocket. Each `stats` message is a
cumulative snapshot for one competitor within one round. It is not an
increment. The feed may deliver the same logical message more than once and may
send a corrected snapshot after a round has ended.

Your task is to connect to the supplied local feed, identify why the totals are
wrong, and make the supplied test pass.

## Requirements

Update `consumer.py` so that it:

1. Connects to the WebSocket and consumes JSON messages.
2. Stops processing after `end_fight`.
3. Ignores repeated sequence numbers. The first occurrence wins.
4. Retains the latest snapshot for each round and competitor.
5. Calculates final fight totals from the retained snapshots.
6. Keeps the public interface `async def consume_feed(url: str) -> dict`.

Add one focused unit test for an edge case you consider important. The added
test should exercise the processing logic independently of the WebSocket.

You may edit `consumer.py` and add tests. Do not edit `mock_feed.py` or weaken
the supplied test.

## Message contract

Every frame is a JSON object with this shape:

```json
{
  "seq": 2,
  "event_id": "fight-101",
  "action": "stats",
  "data": {
    "round": 1,
    "elapsed_seconds": 180,
    "competitor": "red",
    "knockdowns": 0,
    "total_strikes_landed": 12
  }
}
```

- `seq` identifies a logical message. A repeated sequence number is a delivery
  duplicate and must be ignored.
- A genuine correction has a new sequence number.
- A later snapshot for the same round and competitor replaces the earlier one,
  even when a corrected value is lower.
- `start_round`, `round_end`, and `end_fight` are control messages.
- Unknown actions may be ignored.
- The exercise feed contains valid JSON for one event.

## Expected result

```json
{
  "event_id": "fight-101",
  "totals": {
    "red": {
      "knockdowns": 0,
      "total_strikes_landed": 16
    },
    "blue": {
      "knockdowns": 2,
      "total_strikes_landed": 13
    }
  }
}
```

## Setup and tests

Python 3.12 and `uv` are required.

```text
uv sync --frozen
uv run python -m unittest -v
```

The test starts a real local WebSocket server on an automatically selected
port. No separate server process is required for the test.

To inspect the feed manually, use two terminals:

```text
uv run python mock_feed.py
uv run python consumer.py ws://127.0.0.1:8765/feed
```

## Scope

Do not implement automatic reconnection, authentication, TLS, persistence,
Docker, multi-event processing, or a logging framework. These are discussion
topics rather than coding requirements.
