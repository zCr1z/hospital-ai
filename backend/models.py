# backend/models.py

class Room:
    """
    Core domain object.
    Represents a hospital room with attributes and spatial context.
    """

    def __init__(self, room_id, area, zone, attributes, adjacent_to):
        self.id = room_id
        self.area = float(area)
        self.zone = zone
        self.attributes = set(attributes)
        self.adjacent_to = adjacent_to  # list of room IDs

    def has_attr(self, attr):
        return attr in self.attributes


class ComplianceResult:
    """
    Final output item shown to judges.
    One row in the Compliance Report.
    """

    def __init__(self, rule_id, severity, message, source, category):
        self.rule_id = rule_id
        self.severity = severity          # CRITICAL / WARNING
        self.message = message
        self.source = source              # AERB / NBC / NABH / Functional
        self.category = category          # AREA / ADJACENCY / ZONE / FLOW / CONFLICT

    def to_dict(self):
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "message": self.message,
            "source": self.source,
            "category": self.category
        }


class LogEvent:
    """
    Explains HOW the engine is thinking.
    This is what you render in the 'Processing Log' panel.
    """

    def __init__(self, step, rule_id, status, message):
        self.step = step                  # Area Check / Adjacency Check / etc.
        self.rule_id = rule_id
        self.status = status              # PASS / FAIL / CONFLICT
        self.message = message

    def to_dict(self):
        return {
            "step": self.step,
            "rule_id": self.rule_id,
            "status": self.status,
            "message": self.message
        }
