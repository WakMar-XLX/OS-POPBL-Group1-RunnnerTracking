"""Tests for metrics.py. Run with:  python -m pytest

The Round Robin example is worked out by hand (quantum 2, no clearing time):

    Wave  arrival  burst
    A     0        5
    B     1        3
    C     2        1

    Gantt:  A 0-2, B 2-4, C 4-5, A 5-7, B 7-8, A 8-9
    Completion:  A 9, B 8, C 5
    Turnaround:  A 9, B 7, C 3      (completion - arrival)
    Waiting:     A 4, B 4, C 2      (turnaround - burst)
    Response:    A 0, B 1, C 2      (first start - arrival)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from scheduler import Wave, schedule
from metrics import pcb_at, per_wave_metrics

WAVES = [Wave("A", 0, 5, 1, 10), Wave("B", 1, 3, 1, 10), Wave("C", 2, 1, 1, 10)]


def rr():
    return schedule(WAVES, "Round Robin", quantum=2, switch=0)


def test_round_robin_gantt_matches_hand_calculation():
    runs = [(s["wave"], s["start"], s["end"]) for s in rr()["slices"] if s["type"] == "run"]
    assert runs == [(0, 0, 2), (1, 2, 4), (2, 4, 5), (0, 5, 7), (1, 7, 8), (0, 8, 9)]


def test_per_wave_numbers_match_hand_calculation():
    rows = per_wave_metrics(WAVES, rr())
    assert [r["completion"] for r in rows] == [9, 8, 5]
    assert [r["turnaround"] for r in rows] == [9, 7, 3]
    assert [r["waiting"] for r in rows] == [4, 4, 2]
    assert [r["response"] for r in rows] == [0, 1, 2]


def test_waiting_is_turnaround_minus_burst():
    for r in per_wave_metrics(WAVES, rr()):
        assert r["waiting"] == r["turnaround"] - r["burst"]


def test_averages_agree_with_schedule():
    result = rr()
    rows = per_wave_metrics(WAVES, result)
    n = len(rows)
    assert abs(sum(r["waiting"] for r in rows) / n - result["avg_waiting"]) < 1e-9
    assert abs(sum(r["turnaround"] for r in rows) / n - result["avg_turnaround"]) < 1e-9
    assert abs(sum(r["response"] for r in rows) / n - result["avg_response"]) < 1e-9


def test_pcb_at_start():
    rows = pcb_at(WAVES, rr(), 0)
    assert [r["state"] for r in rows] == ["Running", "New", "New"]
    assert [r["remaining"] for r in rows] == [5, 3, 1]


def test_pcb_in_the_middle():
    rows = pcb_at(WAVES, rr(), 3)    # B is running, A and C are waiting
    assert [r["state"] for r in rows] == ["Ready", "Running", "Ready"]
    assert [r["remaining"] for r in rows] == [3, 2, 1]


def test_pcb_at_end():
    rows = pcb_at(WAVES, rr(), 9)
    assert all(r["state"] == "Terminated" and r["remaining"] == 0 for r in rows)
    assert all(r["runners_released"] == r["runners"] for r in rows)


def test_clearing_time_is_counted_as_waiting():
    waves = [Wave("A", 0, 4, 1, 1), Wave("B", 0, 4, 2, 1)]
    result = schedule(waves, "FCFS", switch=2)    # A 0-4, clear 4-6, B 6-10
    rows = per_wave_metrics(waves, result)
    assert rows[1]["waiting"] == 6
