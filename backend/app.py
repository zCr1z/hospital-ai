# backend/app.py

from llm_parser import parse_text_with_llm
from parse_input import parse_architect_input

from rule_engine import (
    load_area_rules,
    load_zone_rules,
    load_adjacency_rules,
    load_flow_rules,
    load_conflict_rules,
    evaluate_area_rules,
    evaluate_zone_transitions,
    evaluate_room_adjacency,
    evaluate_flows,
    detect_conflicts
)

# ==================================================
#           ARCHITECT NATURAL LANGUAGE INPUT
# ==================================================

print("\nDescribe your hospital layout:\n")
user_text = input("> ")

# ---- AI parsing (LLM layer) ----
parsed_json = parse_text_with_llm(user_text)

# ---- Encode JSON → internal models ----
rooms, room_adjacency, flow_paths = parse_architect_input(parsed_json)

# ---- Zone adjacency (simplified for PoC) ----
zone_graph = []
for r1, r2 in room_adjacency:
    zone_graph.append((r1.zone, r2.zone))

# ==================================================
#               LOAD ALL RULES
# ==================================================

area_rules = load_area_rules()
zone_rules = load_zone_rules()
adjacency_rules = load_adjacency_rules()
flow_rules = load_flow_rules()
conflict_rules = load_conflict_rules()

# ==================================================
#               RUN RULE ENGINES
# ==================================================

results = []

results.extend(evaluate_area_rules(rooms, area_rules))
results.extend(evaluate_zone_transitions(zone_graph, zone_rules))
results.extend(evaluate_room_adjacency(rooms, room_adjacency, adjacency_rules))
results.extend(evaluate_flows(flow_paths, flow_rules))

conflicts = detect_conflicts(results, conflict_rules)

# ==================================================
#               FINAL REPORT
# ==================================================

print("\n================ COMPLIANCE REPORT ================\n")

for r in results:
    print(f"[{r.severity}] {r.rule_id}: {r.message} ({r.source})")

for c in conflicts:
    print(f"[CONFLICT] {c.rule_id}: {c.message}")

hard_fail = any(r.severity == "Hard_Fail" for r in results)

print("\n===================================================")

if hard_fail:
    print("❌ FINAL STATUS: LAYOUT REJECTED")
elif conflicts:
    print("⚠️ FINAL STATUS: CONFLICT DETECTED – MANUAL REVIEW REQUIRED")
else:
    print("✅ FINAL STATUS: LAYOUT COMPLIANT")
