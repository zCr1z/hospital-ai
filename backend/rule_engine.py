# backend/rule_engine.py

import csv
import os
from models import ComplianceResult

# ---------------- PATH SETUP ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_DIR = os.path.join(BASE_DIR, "rules")

# ---------------- CSV LOADER ----------------
def load_csv(filename):
    path = os.path.join(RULES_DIR, filename)
    rules = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rules.append(row)

    return rules

# ---------------- AREA RULES ----------------
def evaluate_area_rules(rooms, rules):
    results = []

    for room in rooms:
        for rule in rules:
            if "room_type" not in rule or "min_area" not in rule:
                continue

            if room.name == rule["room_type"]:
                min_area = float(rule["min_area"])

                if room.area < min_area:
                    results.append(
                        ComplianceResult(
                            rule_id=rule.get("rule_id", "AREA_UNKNOWN"),
                            status="FAIL",
                            severity=rule.get("severity", "WARNING"),
                            message=f"{room.name} area too small ({room.area} < {min_area})",
                            source=rule.get("source", "UNKNOWN")
                        )
                    )

    return results

# ---------------- ZONE RULES ----------------
def evaluate_zone_rules(rooms, rules):
    results = []

    for room in rooms:
        for rule in rules:
            if "room_type" not in rule or "required_zone" not in rule:
                continue

            if room.name == rule["room_type"]:
                if room.zone != rule["required_zone"]:
                    results.append(
                        ComplianceResult(
                            rule_id=rule.get("rule_id", "ZONE_UNKNOWN"),
                            status="FAIL",
                            severity=rule.get("severity", "WARNING"),
                            message=f"{room.name} is in {room.zone} zone but must be {rule['required_zone']}",
                            source=rule.get("source", "UNKNOWN")
                        )
                    )

    return results

# ---------------- ADJACENCY RULES ----------------
def evaluate_adjacency_rules(adjacency_map, rules):
    results = []

    for rule in rules:
        if "room_type" not in rule or "forbidden_near" not in rule:
            continue

        room = rule["room_type"]
        forbidden = rule["forbidden_near"]

        if forbidden in adjacency_map.get(room, []):
            results.append(
                ComplianceResult(
                    rule_id=rule.get("rule_id", "ADJ_UNKNOWN"),
                    status="FAIL",
                    severity=rule.get("severity", "CRITICAL"),
                    message=f"{room} placed adjacent to {forbidden}",
                    source=rule.get("source", "UNKNOWN")
                )
            )

    return results

# ---------------- CONFLICT DETECTION ----------------
def detect_conflicts(active_constraints, conflict_rules):
    results = []

    # Even if conflict_rules is empty, detect conflicts dynamically
    for key, values in active_constraints.items():
        unique_values = set(values)

        if len(unique_values) > 1:
            results.append(
                ComplianceResult(
                    rule_id="CONFLICT_DETECTED",
                    status="CONFLICT",
                    severity="CRITICAL",
                    message=f"Conflict detected for {key}: {', '.join(unique_values)}",
                    source="MULTIPLE_REGULATORS"
                )
            )

    return results
