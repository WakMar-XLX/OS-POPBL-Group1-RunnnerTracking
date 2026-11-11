def per_wave_metrics(waves, result):
    """Return one dict per wave with: name, arrival, burst,
    first_start, completion, waiting, turnaround, response."""
"""metrics.py - per-wave metrics and the PCB (process control block) table.

A real operating system keeps one PCB for every process. In WaveFlow every
wave is a process, so each wave gets one row with its id, state, priority,
remaining time and timing numbers.

Two functions are used by the dashboard:
    per_wave_metrics()  final numbers of each wave after the schedule is done
    pcb_at()            the PCB table at one minute of the simulation
"""
from scheduler import runners_released, state_at


def _run_slices(result, k):
    """All Gantt slices where wave k is using the start line."""
    return [s for s in result["slices"] if s["type"] == "run" and s["wave"] == k]


def executed_at(result, k, t):
    """Minutes wave k has already spent on the start line by minute t."""
    return sum(max(0, min(t, s["end"]) - s["start"]) for s in _run_slices(result, k))


def per_wave_metrics(waves, result):
    """Return one dict per wave with the final timing numbers.

    turnaround = completion - arrival
    waiting    = turnaround - burst
    response   = first start - arrival
    """
    rows = []
    for k, w in enumerate(waves):
        first_start = _run_slices(result, k)[0]["start"]
        completion = result["completion"][k]
        turnaround = completion - w.arrival
        rows.append({
            "pid": f"P{k + 1:03d}",
            "name": w.name,
            "arrival": w.arrival,
            "burst": w.burst,
            "first_start": first_start,
            "completion": completion,
            "waiting": turnaround - w.burst,
            "turnaround": turnaround,
            "response": first_start - w.arrival,
        })
    return rows


def pcb_at(waves, result, t):
    """Return the PCB table at minute t, one dict per wave.

    The remaining time is the burst time minus the minutes the wave has
    already spent on the start line.
    """
    rows = []
    for k, w in enumerate(waves):
        rows.append({
            "pid": f"P{k + 1:03d}",
            "name": w.name,
            "state": state_at(waves, result, k, t),
            "priority": w.priority,
            "arrival": w.arrival,
            "burst": w.burst,
            "remaining": w.burst - executed_at(result, k, t),
            "runners_released": runners_released(waves, result, k, t),
            "runners": w.runners,
        })
    return rows
