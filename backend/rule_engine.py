# rule_engine.py
import csv

def load_csv(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))
def check_area_rules(rooms, rules):
    results = []
    for rule in rules:
        for room in rooms:
            if room.name == rule["room_type"]:
                if room.area < float(rule["min_area"]):
                    results.append({
                        "status": "FAIL",
                        "message": f"{room.name} area too small ({room.area} < {rule['min_area']})",
                        "severity": rule["severity"]
                    })
                else:
                    results.append({
                        "status": "PASS",
                        "message": f"{room.name} area OK",
                        "severity": rule["severity"]
                    })
    return results
def check_adjacency_rules(adjacency_map, rules):
    results = []
    for rule in rules:
        room = rule["room_type"]
        forbidden = rule["forbidden_near"]

        if forbidden in adjacency_map.get(room, []):
            results.append({
                "status": "FAIL",
                "message": f"{room} is near {forbidden}",
                "severity": rule["severity"]
            })
    return results
def check_zone_rules(rooms, rules):
    results = []
    for rule in rules:
        for room in rooms:
            if room.name == rule["room_type"]:
                if room.zone != rule["required_zone"]:
                    results.append({
                        "status": "FAIL",
                        "message": f"{room.name} zone mismatch ({room.zone})",
                        "severity": rule["severity"]
                    })
    return results
