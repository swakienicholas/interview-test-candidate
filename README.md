# Live Feed Debugging Exercise

## Overview

A live boxing statistics service is producing incorrect fight totals.

The service receives JSON messages over a WebSocket. Each `stats` message is a
cumulative snapshot for one competitor within one round. It is not an
increment. The feed may deliver the same logical message more than once and may
send a corrected snapshot after a round has ended.

Your task is to connect to the supplied local feed, identify why the totals are
wrong, and make the supplied test pass.

## Deliverables

1. Update `consumer.py` so that `consume_feed()` returns the correct result.
2. If you have time, add one focused unit test for an edge case you consider important.
3. Be ready to explain the defect, your fix, and how you would operate this
   consumer in production.

You may edit `consumer.py` and `test_consumer.py`. Do not edit `mock_feed.py`,
change the expected result, or weaken the supplied integration test.

## Project files

- `consumer.py` - the code you will debug and change.
- `mock_feed.py` - a correct, deterministic local WebSocket server.
- `test_consumer.py` - the supplied integration test and the place for your
  added test.
- `pyproject.toml` and `uv.lock` - the Python version and locked dependency.

## Requirements

Keep the public interface:

```python
async def consume_feed(url: str) -> dict:
    ...
```

It must:

1. Connect to the WebSocket and consume JSON messages.
2. Stop processing when it receives `end_fight`.
3. Ignore repeated sequence numbers. The first occurrence wins.
4. Retain the latest snapshot for each round and competitor.
5. Calculate final fight totals from the retained snapshots.
6. Return the result in the shape shown below.

Keep the implementation small and readable. You do not need to introduce a
framework or a complex class hierarchy.

## Message contract

Every WebSocket frame contains one valid JSON object:

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

### Sequence numbers

- `seq` identifies a logical message.
- A repeated `seq` is a delivery duplicate, even if its contents differ.
- The first occurrence of a sequence number wins.
- A genuine correction has a new sequence number.

### Statistics

- Statistics are cumulative within the specified round; they are snapshots,
  not changes to add to the preceding message.
- A later message for the same round and competitor replaces the earlier
  snapshot.
- A correction replaces the earlier snapshot even when a corrected value is
  lower.
- Fight totals are the sum of the final retained round snapshots.

The fields to total are `knockdowns` and `total_strikes_landed`. The supplied
feed uses the competitors `red` and `blue`.

### Control messages

`start_round` and `round_end` describe the feed lifecycle. A correction can
arrive after `round_end`, so that action does not freeze a round. `end_fight`
ends processing. Unknown actions may be ignored.

The exercise feed contains valid JSON for one event.

## Expected result

For the supplied feed, `consume_feed()` must return:

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

Do not hardcode these values; other inputs following the same contract should
also work.

## Getting started

Run the complete test suite before editing:

```text
uv run python -m unittest -v
```

The supplied test starts a genuine local WebSocket server on an automatically
selected port, calls `consume_feed()`, and closes the server. The test should initially fail with incorrect totals; that is the issue to investigate.

When inspecting the feed, pay attention to the meaning of the values, the combination of round and competitor, repeated sequence numbers, lifecycle actions, and messages arriving after `round_end`.

## Adding your focused test

Use standard-library `unittest`; no additional test framework is required.
Your test should exercise `StatsProcessor` directly rather than starting
another WebSocket server. Construct a small set of messages, call `apply()` for
each one, and assert the result returned by `result()`.

Choose one focused edge case, for example:

- a repeated sequence number;
- a correction received after `round_end`;
- a correction that lowers an earlier value; or
- an unknown action.

Run the suite after each useful change:

```text
uv run python -m unittest -v
```

## Completion checklist

Before finishing, check that:

- the supplied integration test passes;
- additionally, if applicable, your focused unit test passes;
- processing stops at `end_fight`;
- the solution does not hardcode the sample totals or event ID;
- `mock_feed.py` and the supplied assertion remain unchanged; and
- temporary prints or debugging changes have been removed.

