"""Exhaustive bounded state model for two request IDs and one capacity slot."""

from collections import deque


def successors(state):
    # state is a sorted tuple of (request_id, status) pairs.
    records = dict(state)
    for request_id in ("r1", "r2"):
        if request_id not in records and len(records) < 1:
            next_records = dict(records, **{request_id: "held"})
            yield tuple(sorted(next_records.items()))
        if records.get(request_id) == "held":
            next_records = dict(records, **{request_id: "confirmed"})
            yield tuple(sorted(next_records.items()))
            next_records = dict(records)
            del next_records[request_id]
            yield tuple(sorted(next_records.items()))


def check_invariants():
    initial = ()
    seen = {initial}
    pending = deque([initial])
    while pending:
        state = pending.popleft()
        assert sum(status in ("held", "confirmed") for _, status in state) <= 1
        for following in successors(state):
            assert len({request_id for request_id, _ in following}) == len(following)
            if following not in seen:
                seen.add(following)
                pending.append(following)
    return len(seen)


if __name__ == "__main__":
    print(f"checked_states={check_invariants()}")
