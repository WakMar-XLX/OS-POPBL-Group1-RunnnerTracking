"""scheduler.py - core OS scheduling logic for WaveFlow.

Idea: every running wave is a PROCESS and the start line is the CPU.
Only one wave can use the start line at a time, so we schedule them
with FCFS, Round Robin or Priority scheduling.

Time is counted in whole minutes.
"""
from dataclasses import dataclass

ALGOS = ["FCFS", "Round Robin", "Priority"]


@dataclass
class Wave:
    """One wave = one process (its PCB, in OS terms)."""
    name: str
    arrival: int    # minute the wave is ready at the start area
    burst: int      # minutes the wave needs the start line
    priority: int   # 1 = highest priority
    runners: int    # number of runners in the wave


def schedule(waves, algo, quantum=5, switch=1, aging_step=0):
    """Run one scheduling algorithm and return slices plus metrics.

    switch = minutes needed to clear the line between two different
    waves (this is the context switch time).

    aging_step = Priority scheduling only. Every aging_step minutes a wave
    waits in the ready queue, its priority number drops by 1 (so it becomes
    more important). 0 means aging is off.
    """
    n = len(waves)
    t = 0                      # simulation clock
    last = -1                  # wave that used the line last
    remaining = [w.burst for w in waves]
    added = [False] * n        # has the wave joined the ready queue yet?
    joined = [0] * n           # minute the wave last joined the ready queue (for aging)
    ready = []                 # ready queue (list of wave indexes)
    slices = []                # Gantt chart data
    first_start = {}
    completion = {}

    def admit():
        """Move waves that have arrived by time t into the ready queue."""
        for k, w in enumerate(waves):
            if not added[k] and w.arrival <= t:
                added[k] = True
                joined[k] = w.arrival      # it has been waiting since it arrived
                ready.append(k)

    while len(completion) < n:
        admit()
        if not ready:                      # line is idle, jump ahead
            t = min(w.arrival for k, w in enumerate(waves) if not added[k])
            last = -1
            continue

        # Pick the next wave. FCFS and RR take the head of the queue,
        # Priority takes the smallest priority number.
        pick = 0
        if algo == "Priority":
            def effective(k):
                """Priority number after aging (smaller = more important)."""
                if aging_step > 0:
                    return waves[k].priority - (t - joined[k]) // aging_step
                return waves[k].priority
            pick = min(range(len(ready)),
                       key=lambda j: (effective(ready[j]), waves[ready[j]].arrival))
        i = ready.pop(pick)

        # Context switch: clear the line before a different wave starts.
        if last != -1 and last != i and switch > 0:
            slices.append({"type": "switch", "wave": i, "start": t, "end": t + switch})
            t += switch
            admit()

        run = min(quantum, remaining[i]) if algo == "Round Robin" else remaining[i]
        first_start.setdefault(i, t)
        slices.append({"type": "run", "wave": i, "start": t, "end": t + run})
        t += run
        remaining[i] -= run
        last = i
        admit()                            # arrivals go in BEFORE the preempted wave
        if remaining[i] > 0:
            joined[i] = t                  # waiting time for aging restarts
            ready.append(i)                # back of the queue
        else:
            completion[i] = t

    turnaround = [completion[k] - w.arrival for k, w in enumerate(waves)]
    waiting = [turnaround[k] - w.burst for k, w in enumerate(waves)]
    response = [first_start[k] - w.arrival for k, w in enumerate(waves)]
    return {
        "slices": slices,
        "completion": completion,
        "end": t,
        "avg_waiting": sum(waiting) / n,
        "avg_turnaround": sum(turnaround) / n,
        "avg_response": sum(response) / n,
    }


def state_at(waves, result, k, t):
    """Process state of wave k at minute t: New, Ready, Running, Blocked, Terminated."""
    if t < waves[k].arrival:
        return "New"
    if t >= result["completion"][k]:
        return "Terminated"
    for s in result["slices"]:
        if s["start"] <= t < s["end"] and s["wave"] == k:
            return "Running" if s["type"] == "run" else "Blocked"
    return "Ready"


def runners_released(waves, result, k, t):
    """How many runners of wave k have left the line by minute t."""
    done = sum(max(0, min(t, s["end"]) - s["start"])
               for s in result["slices"] if s["type"] == "run" and s["wave"] == k)
    return round(waves[k].runners * done / waves[k].burst)
