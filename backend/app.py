# app.py
from models import Room
from rule_engine import *
# Sample input (later this comes from UI)

rooms = [
    Room("MRI", 20, "CLEAN", vibration_sensitive=True),
    Room("CT", 22, "CLEAN"),
    Room("Waiting", 15, "DIRTY")
]

adjacency_map = {
    "MRI": ["Lift"],
    "CT": ["Waiting"]
}
# Load rules
area_rules = load_csv("rules/area_rules.csv")
adj_rules = load_csv("rules/adjacency_rules.csv")
zone_rules = load_csv("rules/zone_rules.csv")
# Run checks
results = []
results += check_area_rules(rooms, area_rules)
results += check_adjacency_rules(adjacency_map, adj_rules)
results += check_zone_rules(rooms, zone_rules)

for r in results:
    print(r["severity"], "-", r["message"])
