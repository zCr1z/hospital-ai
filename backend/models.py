# backend/models.py

class Room:
    def __init__(self, name, area, zone):
        self.name = name
        self.area = area
        self.zone = zone


class ComplianceResult:
    def __init__(self, rule_id, status, severity, message, source):
        self.rule_id = rule_id
        self.status = status
        self.severity = severity
        self.message = message
        self.source = source

    def to_dict(self):
        return {
            "rule_id": self.rule_id,
            "status": self.status,
            "severity": self.severity,
            "message": self.message,
            "source": self.source
        }
