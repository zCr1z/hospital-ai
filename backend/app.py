# backend/app.py

from models import Room
from rule_engine import (
    load_csv,
    evaluate_area_rules,
    evaluate_zone_rules,
    evaluate_adjacency_rules,
    detect_conflicts
)

# ---------------- SAMPLE INPUT ----------------
rooms = [
    Room("MRI", 22, "CLEAN"),
    Room("CT", 24, "DIRTY"),
    Room("Waiting", 18, "SEMI")
]

# Which rooms are near which
adjacency_map = {
    "MRI": ["Lift"],       # Violation (MRI near Lift)
    "CT": ["Waiting"]      # Usually allowed
}

# Simulated conflicting constraints (NBC vs NABH)
active_constraints = {
    "corridor_access": ["PUBLIC", "RESTRICTED"]
}

# ---------------- LOAD RULES ----------------
area_rules = load_csv("area_rules.csv")
adjacency_rules = load_csv("adjacency_rules.csv")
zone_rules = load_csv("zone_rules.csv")

# Conflict rules are OPTIONAL for now
# We simulate conflicts directly from active_constraints
conflict_rules = []  

# ---------------- RUN ENGINE ----------------
results = []

results.extend(evaluate_area_rules(rooms, area_rules))
results.extend(evaluate_zone_rules(rooms, zone_rules))
results.extend(evaluate_adjacency_rules(adjacency_map, adjacency_rules))
results.extend(detect_conflicts(active_constraints, conflict_rules))

# ---------------- OUTPUT ----------------
print("\n=== COMPLIANCE REPORT ===\n")

if not results:
    print("✅ No compliance issues detected.")
else:
    for r in results:
        print(f"[{r.severity}] {r.message} ({r.source})")
