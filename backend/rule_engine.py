# backend/rule_engine.py

import csv
from pathlib import Path
from models import ComplianceResult, LogEvent


# -------------------------------------------------
# CSV LOADER
# -------------------------------------------------
def load_csv(path: Path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# -------------------------------------------------
# AREA RULES
# -------------------------------------------------
def evaluate_area(rooms, rules, logs):
    results = []
    applied = False

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
                applied = True
                min_area = float(rule["Min_Area_sqm"])

                if room.area < min_area:
                    msg = rule["Explainability_Template"] \
                        .replace("{Actual}", str(room.area)) \
                        .replace("{Min}", str(min_area))

                    logs.append(LogEvent("AREA", rule["Rule_ID"], "FAIL", msg))
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
                    msg = f"{room.id} area {room.area} sqm ≥ {min_area} sqm"
                    logs.append(LogEvent("AREA", rule["Rule_ID"], "PASS", msg))
                    results.append(
                        ComplianceResult(
                            rule_id=rule["Rule_ID"],
                            severity="PASS",
                            message=msg,
                            source=rule["Source"],
                            category="AREA"
                        )
                    )

    if not applied:
        results.append(
            ComplianceResult(
                rule_id="AREA_NONE",
                severity="INFO",
                message="No area rules applicable to given rooms",
                source="SYSTEM",
                category="AREA"
            )
        )

    return results


# -------------------------------------------------
# ADJACENCY RULES
# -------------------------------------------------
def evaluate_adjacency(rooms, rules, logs):
    results = []
    room_map = {r.id: r for r in rooms}
    applied = False

    logs.append(LogEvent(
        step="ADJACENCY",
        rule_id="ADJ_INIT",
        status="INFO",
        message="Starting adjacency compliance checks"
    ))

    for rule in rules:
        for room in rooms:
            if room.has_attr(rule["Primary_Room_Attribute"]):
                applied = True
                for adj_id in room.adjacent_to:
                    adj_room = room_map.get(adj_id)
                    if not adj_room:
                        continue

                    if adj_room.has_attr(rule["Adjacent_Room_Attribute"]):
                        if rule["Adjacency_Allowed"] == "No":
                            logs.append(LogEvent(
                                "ADJACENCY",
                                rule["Rule_ID"],
                                "FAIL",
                                rule["Reason"]
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
                                "ADJACENCY",
                                rule["Rule_ID"],
                                "PASS",
                                "Adjacency allowed"
                            ))

    if not applied:
        results.append(
            ComplianceResult(
                rule_id="ADJ_NONE",
                severity="INFO",
                message="No adjacency rules applicable",
                source="SYSTEM",
                category="ADJACENCY"
            )
        )

    return results


# -------------------------------------------------
# ZONE RULES
# -------------------------------------------------
def evaluate_zone(rooms, rules, logs):
    results = []
    room_map = {r.id: r for r in rooms}
    applied = False

    logs.append(LogEvent(
        step="ZONE",
        rule_id="ZONE_INIT",
        status="INFO",
        message="Starting zone transition checks"
    ))

    for rule in rules:
        for room in rooms:
            if (
                room.zone == rule["Primary_Zone"]
                and room.has_attr(rule["Primary_Room_Attribute"])
            ):
                for adj_id in room.adjacent_to:
                    adj_room = room_map.get(adj_id)
                    if not adj_room:
                        continue

                    if (
                        adj_room.zone == rule["Secondary_Zone"]
                        and adj_room.has_attr(rule["Secondary_Room_Attribute"])
                        and rule["Transition_Allowed"] == "No"
                    ):
                        applied = True
                        logs.append(LogEvent(
                            "ZONE",
                            rule["Rule_ID"],
                            "FAIL",
                            rule["Reason"]
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

    if not applied:
        results.append(
            ComplianceResult(
                rule_id="ZONE_NONE",
                severity="INFO",
                message="No zone conflicts detected",
                source="SYSTEM",
                category="ZONE"
            )
        )

    return results


# -------------------------------------------------
# FLOW RULES
# -------------------------------------------------
def evaluate_flow(layout, rules, logs):
    results = []
    applied = False

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

            applied = True
            if (
                rule["Flow_Allowed"] == "No"
                and rule["Origin_Zone"] in path_zones
                and rule["Destination_Zone"] in path_zones
            ):
                logs.append(LogEvent(
                    "FLOW",
                    rule["Rule_ID"],
                    "FAIL",
                    rule["Reason"]
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

    if not applied:
        results.append(
            ComplianceResult(
                rule_id="FLOW_NONE",
                severity="INFO",
                message="No flow rules applicable",
                source="SYSTEM",
                category="FLOW"
            )
        )

    return results


# -------------------------------------------------
# CONFLICT RULES
# -------------------------------------------------
def evaluate_conflicts(rooms, rules, logs):
    results = []
    active_attributes = set()

    logs.append(LogEvent(
        step="CONFLICT",
        rule_id="CONFLICT_INIT",
        status="INFO",
        message="Starting regulatory conflict detection"
    ))

    # Collect all active attributes
    for room in rooms:
        active_attributes.update(room.attributes)

    for rule in rules:
        if (
            rule["Constraint_A"] in active_attributes
            and rule["Constraint_B"] in active_attributes
        ):
            logs.append(LogEvent(
                "CONFLICT",
                rule["Conflict_ID"],
                "CONFLICT",
                rule["Conflict_Description"]
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

    if not results:
        results.append(
            ComplianceResult(
                rule_id="CONFLICT_NONE",
                severity="INFO",
                message="No regulatory conflicts detected",
                source="SYSTEM",
                category="CONFLICT"
            )
        )

    return results
