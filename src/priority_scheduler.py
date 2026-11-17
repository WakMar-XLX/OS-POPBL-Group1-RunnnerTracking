class Runner:
    def __init__(self, runner_id, category_priority, distance_km):
        self.runner_id = runner_id         # Participant ID / Bib Number
        self.priority = category_priority  # Priority Level (e.g., 3=VIP/OKU/Medical, 2=Senior, 1=Open)
        self.burst_time = distance_km      # Distance or service duration required
        self.waiting_time = 0              # Time spent waiting in the queue

def community_run_scheduler(runners):
    print("==================================================")
    print("      COMMUNITY RUN PARTICIPANT SCHEDULER         ")
    print("==================================================")
    
    step = 1
    while runners:
        # Sort runners by highest priority first (higher number = higher priority)
        runners.sort(key=lambda x: x.priority, reverse=True)
        
        print(f"\n--- Simulation Step {step} ---")
        print("Current Queue Status:")
        for r in runners:
            print(f" -> Bib #{r.runner_id} | Priority: {r.priority} | Waiting Time: {r.waiting_time}")
            
        # Pop the runner with the highest priority from the front of the queue
        current_runner = runners.pop(0)
        print(f"\n[PROCESSING] Attending / Flagging off **Bib #{current_runner.runner_id}** (Current Priority: {current_runner.priority})")
        
        # Aging Mechanism: Increment waiting time for remaining runners and boost priority if waiting too long
        for r in runners:
            r.waiting_time += 1
            # If waiting for 2 or more steps, increase priority to prevent starvation
            if r.waiting_time >= 2 and r.priority < 3:
                r.priority += 1
                print(f"   -> [AGING ALERT] Bib #{r.runner_id} has waited too long. Priority boosted to **{r.priority}**!")
                
        step += 1

# --- MAIN EXECUTION / TEST SIMULATION ---
if __name__ == "__main__":
    # Sample participants with different priority categories
    # Priority Legend: 1 = Open Category, 2 = Veteran/Senior, 3 = Special Assistance / VIP / Emergency
    run_participants = [
        Runner(runner_id=101, category_priority=1, distance_km=5),
        Runner(runner_id=102, category_priority=3, distance_km=2),
        Runner(runner_id=103, category_priority=2, distance_km=4)
    ]
    
    community_run_scheduler(run_participants)
