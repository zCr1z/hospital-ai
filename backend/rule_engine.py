# backend/rule_engine.py

import csv
import os

from models import (
    ComplianceResult,
    AreaRule,
    ZoneTransitionRule,
    AdjacencyRule,
    FlowRule,
    ConflictRule
)


def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# ---------------- PATH SETUP ----------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_DIR = os.path.join(BASE_DIR, "rules")

# ---------------- GENERIC CSV LOADER ----------------

def load_csv(filename):
    path = os.path.join(RULES_DIR, filename)
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ==================================================
#                RULE LOADERS
# ==================================================

def load_area_rules():
    rules = []
    rows = load_csv("rooms.csv")  # area rules CSV

    for r in rows:
        rules.append(
            AreaRule(
                rule_id=r["Rule_ID"],
                source=r["Source"],
                room_attribute=r["Room_Attribute"],
                min_val=safe_float(r["Min_Area_sqm"]),
                max_val=safe_float(r["Max_Area_sqm"]),
                applies_to=r["Applies_To"],
                severity=r["Severity"],
                action=r["Action_On_Violation"],
                template=r["Explainability_Template"]
            )
)

    return rules


def load_zone_rules():
    rules = []
    rows = load_csv("zone_rules.csv")

    for r in rows:
        rules.append(
            ZoneTransitionRule(
                rule_id=r["Rule_ID"],
                source=r["Source"],
                primary_zone=r["Primary_Zone"],
                secondary_zone=r["Secondary_Zone"],
                allowed=r["Transition_Allowed"],
                buffer_required=r["Buffer_Required"],
                severity=r["Severity"],
                action=r["Action_On_Violation"],
                template=r["Explainability_Template"]
            )
        )
    return rules


def load_adjacency_rules():
    rules = []
    rows = load_csv("adjacency_rules.csv")

    for r in rows:
        rules.append(
            AdjacencyRule(
                rule_id=r["Rule_ID"],
                source=r["Source"],
                primary_attr=r["Primary_Room_Attribute"],
                adjacent_attr=r["Adjacent_Room_Attribute"],
                allowed_type=r["Adjacency_Allowed"],
                severity=r["Severity"],
                action=r["Action_On_Violation"]
            )
        )
    return rules


def load_flow_rules():
    rules = []
    rows = load_csv("flow_rules.csv")

    for r in rows:
        intermediates = []
        if r["Intermediate_Zone_Required"] and r["Intermediate_Zone_Required"] != "None":
            intermediates = r["Intermediate_Zone_Required"].split("|")

        rules.append(
            FlowRule(
                rule_id=r["Rule_ID"],
                source=r["Source"],
                origin_zone=r["Origin_Zone"],
                dest_zone=r["Destination_Zone"],
                entity=r["Flow_Entity"],
                allowed=r["Flow_Allowed"],
                intermediates=intermediates,
                severity=r["Severity"],
                action=r["Action_On_Violation"],
                template=r["Explainability_Template"]
            )
        )
    return rules


def load_conflict_rules():
    rules = []
    rows = load_csv("conflict_rules.csv")

    for r in rows:
        rules.append(
            ConflictRule(
                conflict_id=r["Conflict_ID"],
                reg_a=r["Primary_Regulation"],
                reg_b=r["Secondary_Regulation"],
                attr_a=r["Trigger_Condition_Attribute_A"],
                attr_b=r["Trigger_Condition_Attribute_B"],
                severity=r["Severity"],
                priority=r["Resolution_Priority"],
                action=r["System_Action"],
                template=r["Explainability_Template"]
            )
        )
    return rules


# ==================================================
#              EVALUATION ENGINES
# ==================================================

def evaluate_area_rules(rooms, area_rules):
    """
    Area / dimension compliance.
    """
    results = []

    for room in rooms:
        for rule in area_rules:
            if rule.room_attribute in room.attributes:
                if rule.min_val is not None and room.area < rule.min_val:
                    results.append(
                        ComplianceResult(
                            rule_id=rule.rule_id,
                            status="FAIL",
                            severity=rule.severity,
                            message=rule.template.format(
                                Actual=room.area,
                                Min=rule.min_val,
                                Max=rule.max_val
                            ),
                            source=rule.source,
                            action=rule.action
                        )
                    )
    return results


def evaluate_zone_transitions(zone_graph, zone_rules):
    """
    Zone → Zone adjacency validation.
    """
    results = []

    for (z1, z2) in zone_graph:
        for rule in zone_rules:
            if rule.primary_zone == z1 and rule.secondary_zone == z2:
                if rule.allowed == "No":
                    results.append(
                        ComplianceResult(
                            rule_id=rule.rule_id,
                            status="FAIL",
                            severity=rule.severity,
                            message=rule.template,
                            source=rule.source,
                            action=rule.action
                        )
                    )
    return results


def evaluate_room_adjacency(rooms, adjacency_graph, adjacency_rules):
    """
    Attribute-based room adjacency validation.
    """
    results = []
    seen = set()   # <-- prevents duplicate reporting

    for r1, r2 in adjacency_graph:
        for rule in adjacency_rules:
            if (
                rule.primary_attr in r1.attributes and
                rule.adjacent_attr in r2.attributes and
                rule.allowed_type == "No"
            ):
                key = (r1.name, r2.name, rule.rule_id)
                if key in seen:
                    continue
                seen.add(key)

                results.append(
                    ComplianceResult(
                        rule_id=rule.rule_id,
                        status="FAIL",
                        severity=rule.severity,
                        message=f"{r1.name} adjacent to {r2.name}",
                        source=rule.source,
                        action=rule.action
                    )
                )
    return results



def evaluate_flows(flow_paths, flow_rules):
    """
    Entity flow validation (path-based).
    """
    results = []

    for path in flow_paths:
        for rule in flow_rules:
            if (
                path["entity"] == rule.entity and
                path["origin"] == rule.origin_zone and
                path["destination"] == rule.dest_zone
            ):
                if rule.allowed == "No":
                    results.append(
                        ComplianceResult(
                            rule_id=rule.rule_id,
                            status="FAIL",
                            severity=rule.severity,
                            message=rule.template,
                            source=rule.source,
                            action=rule.action
                        )
                    )
    return results


def detect_conflicts(results, conflict_rules):
    """
    Meta-rule engine: detects regulatory conflicts.
    """
    conflicts = []

    triggered_attrs = set()
    for r in results:
        triggered_attrs.add(r.rule_id)

    for rule in conflict_rules:
        if rule.attr_a in triggered_attrs and rule.attr_b in triggered_attrs:
            conflicts.append(
                ComplianceResult(
                    rule_id=rule.conflict_id,
                    status="CONFLICT",
                    severity=rule.severity,
                    message=rule.template,
                    source=f"{rule.reg_a} vs {rule.reg_b}",
                    action=rule.action
                )
            )

    return conflicts
