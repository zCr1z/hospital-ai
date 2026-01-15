# backend/models.py

# ---------------- CORE DOMAIN MODELS ----------------

class Room:
    """
    Represents a physical room/space in the layout.
    """
    def __init__(self, name, area, zone, room_type=None, attributes=None):
        self.name = name                  # e.g. "MRI Room 1"
        self.room_type = room_type or name  # e.g. "MRI", "CT", "Waiting"
        self.area = area                  # numeric (sqm)
        self.zone = zone                  # e.g. Clean_Zone, MRI_Zone_III
        self.attributes = set(attributes) if attributes else set()

    def has_attribute(self, attr):
        return attr in self.attributes


# ---------------- RESULT MODEL (KEEP & EXTEND) ----------------

class ComplianceResult:
    """
    Standard output unit for all rule engines.
    """
    def __init__(self, rule_id, status, severity, message, source, action=None):
        self.rule_id = rule_id
        self.status = status              # PASS / FAIL / WARNING / CONFLICT
        self.severity = severity          # Hard_Fail / Warning / Critical / Major
        self.message = message
        self.source = source              # AERB / NABH / NBC / Functional
        self.action = action              # Reject_Layout / Suggest_Optimization / Flag_Conflict

    def to_dict(self):
        return {
            "rule_id": self.rule_id,
            "status": self.status,
            "severity": self.severity,
            "message": self.message,
            "source": self.source,
            "action": self.action
        }


# ---------------- RULE MODELS (LIGHTWEIGHT) ----------------
# These are intentionally simple containers (not heavy OOP)

class AreaRule:
    def __init__(self, rule_id, source, room_attribute, min_val, max_val,
                 applies_to, severity, action, template):
        self.rule_id = rule_id
        self.source = source
        self.room_attribute = room_attribute
        self.min_val = min_val
        self.max_val = max_val
        self.applies_to = applies_to
        self.severity = severity
        self.action = action
        self.template = template


class ZoneTransitionRule:
    def __init__(self, rule_id, source, primary_zone, secondary_zone,
                 allowed, buffer_required, severity, action, template):
        self.rule_id = rule_id
        self.source = source
        self.primary_zone = primary_zone
        self.secondary_zone = secondary_zone
        self.allowed = allowed              # Yes / No / Conflict
        self.buffer_required = buffer_required
        self.severity = severity
        self.action = action
        self.template = template


class AdjacencyRule:
    def __init__(self, rule_id, source, primary_attr, adjacent_attr,
                 allowed_type, severity, action):
        self.rule_id = rule_id
        self.source = source
        self.primary_attr = primary_attr
        self.adjacent_attr = adjacent_attr
        self.allowed_type = allowed_type    # Yes / No / Indirect_Only / Preferred
        self.severity = severity
        self.action = action


class FlowRule:
    def __init__(self, rule_id, source, origin_zone, dest_zone, entity,
                 allowed, intermediates, severity, action, template):
        self.rule_id = rule_id
        self.source = source
        self.origin_zone = origin_zone
        self.dest_zone = dest_zone
        self.entity = entity
        self.allowed = allowed
        self.intermediates = intermediates  # list
        self.severity = severity
        self.action = action
        self.template = template


class ConflictRule:
    def __init__(self, conflict_id, reg_a, reg_b, attr_a, attr_b,
                 severity, priority, action, template):
        self.conflict_id = conflict_id
        self.reg_a = reg_a
        self.reg_b = reg_b
        self.attr_a = attr_a
        self.attr_b = attr_b
        self.severity = severity
        self.priority = priority
        self.action = action
        self.template = template
