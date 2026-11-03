---
name: reservation-verification
description: Check the reservation capacity invariant after changes to ReservationBook.
---

# Reservation verification

Coverage: `ReservationBook.create`, `ReservationBook.confirm`, and `ReservationBook.cancel` in `reservation.py`.

Property: held plus confirmed reservations never exceed `capacity`, and one request has at most one state. The bounded model explores two request IDs and capacity one in `verification/reservation_model.py`.

Run `python3 verification/reservation_model.py` and `python3 -m unittest discover -s tests`. Check the model's transitions against the current implementation before accepting a result. Sync commit: baseline only. If you verify an uncommitted refactor, keep this commit unchanged and record the dirty worktree paths and checks separately; only advance this commit after the verified code is committed.
