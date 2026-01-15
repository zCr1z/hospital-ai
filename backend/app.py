from rule_engine import run_engine
import csv
from pathlib import Path


def load_allowed_values(rules_path):
    attrs = set()
    zones = set()

    import csv
    from pathlib import Path

    for file in ["adjacency_rules.csv", "area_rules.csv", "conflict_rules.csv"]:
        with open(Path(rules_path) / file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                for k, v in row.items():
                    if k and "Attribute" in k and v:
                        attrs.add(v)

    with open(Path(rules_path) / "zone_rules.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r.get("Primary_Zone"):
                zones.add(r["Primary_Zone"])
            if r.get("Secondary_Zone"):
                zones.add(r["Secondary_Zone"])

    return sorted(attrs), sorted(zones)


def get_user_layout():
    rooms = []
    flows = []

    allowed_attrs, allowed_zones = load_allowed_values("./rules")

    print("\n--- ALLOWED ATTRIBUTES ---")
    print(", ".join(allowed_attrs))

    print("\n--- ALLOWED ZONES ---")
    print(", ".join(allowed_zones))

    n = int(input("\nEnter number of rooms: "))

    for i in range(n):
        print(f"\nRoom {i + 1}")
        room_id = input("Room ID: ")
        area = float(input("Area (sqm): "))
        zone = input("Zone: ")
        attributes = input("Attributes (comma separated): ").split(",")
        adjacent = input("Adjacent rooms (comma separated): ").split(",")

        rooms.append({
            "id": room_id.strip(),
            "area": area,
            "zone": zone.strip(),
            "attributes": [a.strip() for a in attributes if a.strip()],
            "adjacent_to": [a.strip() for a in adjacent if a.strip()]
        })

    add_flow = input("\nAdd patient flow? (y/n): ").lower()
    if add_flow == "y":
        path = input("Flow path (comma separated room IDs): ").split(",")
        flows.append({
            "entity": "Patient",
            "path": [p.strip() for p in path if p.strip()]
        })

    return {
        "rooms": rooms,
        "flows": flows
    }


if __name__ == "__main__":
    layout = get_user_layout()
    results = run_engine(layout, "./rules")

    print("\n--- RULE ENGINE OUTPUT ---")
    if results:
        for r in results:
            print(r)
    else:
        print("No violations detected")
