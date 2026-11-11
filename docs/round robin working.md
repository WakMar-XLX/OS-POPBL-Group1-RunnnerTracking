[round-robin-working.md](https://github.com/user-attachments/files/34672474/round-robin-working.md)

# Round Robin: Hand Calculations

Group 1, WaveFlow. These examples were worked out on paper first and then checked against `schedule()` in `src/scheduler.py` and `per_wave_metrics()` in `src/metrics.py`. The same numbers appear in `tests/test_metrics.py`.

## Formulas

- Completion: the minute the last runner of the wave has left the start line.
- Turnaround time = completion - arrival
- Waiting time = turnaround - burst
- Response time = first start - arrival

Burst is the number of minutes a wave needs the start line. A wave that has used its time quantum without finishing goes to the back of the ready queue. When a different wave takes the line, the line is cleared first, and that clearing time counts as waiting for every wave that is not running.

## Example 1: quantum 2, no clearing time

| Wave | Arrival | Burst |
|---|---|---|
| A | 0 | 5 |
| B | 1 | 3 |
| C | 2 | 1 |

Step by step:

| Clock | Ready queue before the pick | Wave picked | Runs | Remaining after | Queue after |
|---|---|---|---|---|---|
| 0 | A | A | 0 to 2 | 3 | B, C, A |
| 2 | B, C, A | B | 2 to 4 | 1 | C, A, B |
| 4 | C, A, B | C | 4 to 5 | 0 (done) | A, B |
| 5 | A, B | A | 5 to 7 | 1 | B, A |
| 7 | B, A | B | 7 to 8 | 0 (done) | A |
| 8 | A | A | 8 to 9 | 0 (done) | empty |

B and C arrive while A is running, so they join the queue before A goes back to the end of it.

Gantt chart: A 0-2, B 2-4, C 4-5, A 5-7, B 7-8, A 8-9.

| Wave | Completion | Turnaround | Waiting | Response |
|---|---|---|---|---|
| A | 9 | 9 - 0 = 9 | 9 - 5 = 4 | 0 - 0 = 0 |
| B | 8 | 8 - 1 = 7 | 7 - 3 = 4 | 2 - 1 = 1 |
| C | 5 | 5 - 2 = 3 | 3 - 1 = 2 | 4 - 2 = 2 |

Averages: waiting 3.33, turnaround 6.33, response 1.0 minutes.

### Comparison with FCFS on the same waves

FCFS runs A 0-5, B 5-8, C 8-9.

| Wave | Completion | Turnaround | Waiting | Response |
|---|---|---|---|---|
| A | 5 | 5 | 0 | 0 |
| B | 8 | 7 | 4 | 4 |
| C | 9 | 7 | 6 | 6 |

Averages: waiting 3.33, turnaround 6.33, response 3.33 minutes.

Waiting and turnaround come out the same in this small example, but the average response time is 3.33 minutes with FCFS and 1.0 with Round Robin. Every wave gets a turn on the start line sooner, which is what we want when several categories are waiting in the warm-up area.

## Example 2: quantum 3, clearing time 1 minute

| Wave | Arrival | Burst |
|---|---|---|
| A | 0 | 7 |
| B | 1 | 4 |
| C | 2 | 2 |

Step by step (clearing slices are marked "clear"):

| Clock | What happens | Queue after |
|---|---|---|
| 0 to 3 | A runs 3 minutes, 4 left | B, C, A |
| 3 to 4 | clear the line for B | |
| 4 to 7 | B runs 3 minutes, 1 left | C, A, B |
| 7 to 8 | clear the line for C | |
| 8 to 10 | C runs 2 minutes, done | A, B |
| 10 to 11 | clear the line for A | |
| 11 to 14 | A runs 3 minutes, 1 left | B, A |
| 14 to 15 | clear the line for B | |
| 15 to 16 | B runs 1 minute, done | A |
| 16 to 17 | clear the line for A | |
| 17 to 18 | A runs 1 minute, done | empty |

| Wave | Completion | Turnaround | Waiting | Response |
|---|---|---|---|---|
| A | 18 | 18 - 0 = 18 | 18 - 7 = 11 | 0 - 0 = 0 |
| B | 16 | 16 - 1 = 15 | 15 - 4 = 11 | 4 - 1 = 3 |
| C | 10 | 10 - 2 = 8 | 8 - 2 = 6 | 8 - 2 = 6 |

Averages: waiting 9.33, turnaround 13.67, response 3.0 minutes.

## What the examples show

1. The quantum controls how often waves swap. A small quantum gives a fair share of the line but adds more clearing time, as the second example shows: 5 of the 18 minutes were spent clearing the line.
2. Clearing time is a cost. With a clearing time of 0, Round Robin is cheap to run, but on a real start line every swap takes time.
3. Round Robin gives a short average response time, so no wave waits a long time before it first reaches the start line.
