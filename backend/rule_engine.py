# backend/rule_engine.py

import csv
from pathlib import Path
from models import ComplianceResult, LogEvent


# -------------------------------------------------
# CSV LOADER
# -------------------------------------------------
def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# -------------------------------------------------
# AREA RULES
# -------------------------------------------------
def evaluate_area(rooms, rules, logs):
    results = []

    logs.append(LogEvent(
        step="AREA",
        rule_id="AREA_INIT",
        status="INFO",
        message="Starting area compliance checks"
    ))

    for rule in rules:
        for room in rooms:
            attr = rule.get("Room_Attribute")
            if attr and room.has_attr(attr):
                min_area = rule.get("Min_Area_sqm")

                if min_area and room.area < float(min_area):
                    msg = rule["Explainability_Template"] \
                        .replace("{Actual}", str(room.area)) \
                        .replace("{Min}", min_area)

                    logs.append(LogEvent(
                        step="AREA",
                        rule_id=rule["Rule_ID"],
                        status="FAIL",
                        message=msg
                    ))

                    results.append(
                        ComplianceResult(
                            rule_id=rule["Rule_ID"],
                            severity=rule["Severity"],
                            message=msg,
                            source=rule["Source"],
                            category="AREA"
                        )
                    )
                else:
                    logs.append(LogEvent(
                        step="AREA",
                        rule_id=rule["Rule_ID"],
                        status="PASS",
                        message=f"{room.id} satisfies minimum area"
                    ))

    return results


# -------------------------------------------------
# ADJACENCY RULES
# -------------------------------------------------
def evaluate_adjacency(rooms, rules, logs):
    results = []
    room_map = {r.id: r for r in rooms}

    logs.append(LogEvent(
        step="ADJACENCY",
        rule_id="ADJ_INIT",
        status="INFO",
        message="Starting adjacency compliance checks"
    ))

    for rule in rules:
        for room in rooms:
            if room.has_attr(rule["Primary_Room_Attribute"]):
                for adj_id in room.adjacent_to:
                    adj_room = room_map.get(adj_id)
                    if not adj_room:
                        continue

                    if adj_room.has_attr(rule["Adjacent_Room_Attribute"]):
                        if rule["Adjacency_Allowed"] == "No":
                            logs.append(LogEvent(
                                step="ADJACENCY",
                                rule_id=rule["Rule_ID"],
                                status="FAIL",
                                message=rule["Reason"]
                            ))

                            results.append(
                                ComplianceResult(
                                    rule_id=rule["Rule_ID"],
                                    severity=rule["Severity"],
                                    message=rule["Reason"],
                                    source=rule["Source"],
                                    category="ADJACENCY"
                                )
                            )
                        else:
                            logs.append(LogEvent(
                                step="ADJACENCY",
                                rule_id=rule["Rule_ID"],
                                status="PASS",
                                message="Adjacency allowed"
                            ))

    return results


# -------------------------------------------------
# ZONE RULES
# -------------------------------------------------
def evaluate_zone(rooms, rules, logs):
    results = []
    room_map = {r.id: r for r in rooms}

    logs.append(LogEvent(
        step="ZONE",
        rule_id="ZONE_INIT",
        status="INFO",
        message="Starting zone transition checks"
    ))

    for rule in rules:
        for room in rooms:
            for adj_id in room.adjacent_to:
                adj_room = room_map.get(adj_id)
                if not adj_room:
                    continue

                if (room.zone == rule["Primary_Zone"] and
                    adj_room.zone == rule["Secondary_Zone"] and
                    rule["Transition_Allowed"] == "No"):

                    logs.append(LogEvent(
                        step="ZONE",
                        rule_id=rule["Rule_ID"],
                        status="FAIL",
                        message=rule["Reason"]
                    ))

                    results.append(
                        ComplianceResult(
                            rule_id=rule["Rule_ID"],
                            severity=rule["Severity"],
                            message=rule["Reason"],
                            source=rule["Source"],
                            category="ZONE"
                        )
                    )

    return results


# -------------------------------------------------
# FLOW RULES
# -------------------------------------------------
def evaluate_flow(layout, rules, logs):
    results = []

    logs.append(LogEvent(
        step="FLOW",
        rule_id="FLOW_INIT",
        status="INFO",
        message="Starting flow compliance checks"
    ))

    for flow in layout.get("flows", []):
        path_zones = [
            r["zone"] for r in layout["rooms"]
            if r["id"] in flow["path"]
        ]

        for rule in rules:
            if flow["entity"] != rule["Flow_Entity"]:
                continue

            if (rule["Flow_Allowed"] == "No" and
                rule["Origin_Zone"] in path_zones and
                rule["Destination_Zone"] in path_zones):

                logs.append(LogEvent(
                    step="FLOW",
                    rule_id=rule["Rule_ID"],
                    status="FAIL",
                    message=rule["Reason"]
                ))

                results.append(
                    ComplianceResult(
                        rule_id=rule["Rule_ID"],
                        severity=rule["Severity"],
                        message=rule["Reason"],
                        source=rule["Source"],
                        category="FLOW"
                    )
                )

            required = rule.get("Intermediate_Zone_Required")
            if required and required not in path_zones:
                logs.append(LogEvent(
                    step="FLOW",
                    rule_id=rule["Rule_ID"],
                    status="FAIL",
                    message=rule["Explainability_Template"]
                ))

                results.append(
                    ComplianceResult(
                        rule_id=rule["Rule_ID"],
                        severity=rule["Severity"],
                        message=rule["Explainability_Template"],
                        source=rule["Source"],
                        category="FLOW"
                    )
                )

    return results


# -------------------------------------------------
# CONFLICT RULES
# -------------------------------------------------
def evaluate_conflicts(rooms, rules, logs):
    results = []

    logs.append(LogEvent(
        step="CONFLICT",
        rule_id="CONFLICT_INIT",
        status="INFO",
        message="Starting regulatory conflict detection"
    ))

    for rule in rules:
        for room in rooms:
            if (room.has_attr(rule["Trigger_Condition_Attribute_A"]) and
                room.has_attr(rule["Trigger_Condition_Attribute_B"])):

                logs.append(LogEvent(
                    step="CONFLICT",
                    rule_id=rule["Conflict_ID"],
                    status="CONFLICT",
                    message=rule["Conflict_Description"]
                ))

                results.append(
                    ComplianceResult(
                        rule_id=rule["Conflict_ID"],
                        severity=rule["Severity"],
                        message=rule["Conflict_Description"],
                        source=rule["Source"],
                        category="CONFLICT"
                    )
                )

    return results
