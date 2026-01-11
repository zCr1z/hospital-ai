# models.py

class Room:
    def __init__(self, name, area, zone, vibration_sensitive=False):
        self.name = name
        self.area = area
        self.zone = zone
        self.vibration_sensitive = vibration_sensitive
