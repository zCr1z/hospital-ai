import csv
from pathlib import Path

# ---------- LOADERS ----------
def load_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

# ---------- HELPERS ----------
def has_attr(room, attr):
    return attr in room.get("attributes", [])

# ---------- ADJACENCY ----------
def evaluate_adjacency(layout, rules):
    violations = []
    rooms = {r["id"]: r for r in layout["rooms"]}

    for rule in rules:
        for room in rooms.values():
            if has_attr(room, rule["Primary_Room_Attribute"]):
                for adj in room.get("adjacent_to", []):
                    adj_room = rooms.get(adj)
                    if adj_room and has_attr(adj_room, rule["Adjacent_Room_Attribute"]):
                        if rule["Adjacency_Allowed"] == "No":
                            violations.append({
                                "rule_id": rule["Rule_ID"],
                                "severity": rule["Severity"],
                                "message": rule["Reason"]
                            })
    return violations

# ---------- AREA ----------
def evaluate_area(layout, rules):
    violations = []
    for room in layout["rooms"]:
        for rule in rules:
            if rule["Room_Attribute"] in room["attributes"]:
                min_area = rule["Min_Area_sqm"]
                if min_area and room["area"] < float(min_area):
                    msg = rule["Explainability_Template"] \
                        .replace("{Actual}", str(room["area"])) \
                        .replace("{Min}", min_area)
                    violations.append({
                        "rule_id": rule["Rule_ID"],
                        "severity": rule["Severity"],
                        "message": msg
                    })
    return violations

# ---------- ZONE ----------
def evaluate_zone(layout, rules):
    violations = []
    rooms = {r["id"]: r for r in layout["rooms"]}

    for rule in rules:
        for room in rooms.values():
            for adj in room.get("adjacent_to", []):
                adj_room = rooms.get(adj)
                if not adj_room:
                    continue
                if (room["zone"] == rule["Primary_Zone"] and
                    adj_room["zone"] == rule["Secondary_Zone"] and
                    rule["Transition_Allowed"] == "No"):
                    violations.append({
                        "rule_id": rule["Rule_ID"],
                        "severity": rule["Severity"],
                        "message": rule["Reason"]
                    })
    return violations

# ---------- FLOW ----------
def evaluate_flow(layout, rules):
    violations = []

    for flow in layout.get("flows", []):
        path_zones = [room["zone"] for room in layout["rooms"] if room["id"] in flow["path"]]

        for rule in rules:
            if flow["entity"] != rule["Flow_Entity"]:
                continue

            if (rule["Flow_Allowed"] == "No" and
                rule["Destination_Zone"] in path_zones and
                rule["Origin_Zone"] in path_zones):
                violations.append({
                    "rule_id": rule["Rule_ID"],
                    "severity": rule["Severity"],
                    "message": rule["Reason"]
                })

            required = rule.get("Intermediate_Zone_Required")
            if required and required not in path_zones:
                violations.append({
                    "rule_id": rule["Rule_ID"],
                    "severity": rule["Severity"],
                    "message": rule["Explainability_Template"]
                })
    return violations

# ---------- CONFLICT ----------
def evaluate_conflicts(layout, rules):
    conflicts = []
    for rule in rules:
        for room in layout["rooms"]:
            if (rule["Trigger_Condition_Attribute_A"] in room["attributes"] and
                rule["Trigger_Condition_Attribute_B"] in room["attributes"]):
                conflicts.append({
                    "conflict_id": rule["Conflict_ID"],
                    "severity": rule["Severity"],
                    "message": rule["Conflict_Description"]
                })
    return conflicts

# ---------- RUN ENGINE ----------
def run_engine(layout, base_path):
    results = []
    
    base_path = Path(base_path)

    results += evaluate_adjacency(
        layout, load_csv(base_path / "adjacency_rules.csv")
    )
    results += evaluate_area(
        layout, load_csv(base_path / "area_rules.csv")
    )
    results += evaluate_zone(
        layout, load_csv(base_path / "zone_rules.csv")
    )
    results += evaluate_flow(
        layout, load_csv(base_path / "flow_rules.csv")
    )
    results += evaluate_conflicts(
        layout, load_csv(base_path / "conflict_rules.csv")
    )

    return results
