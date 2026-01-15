from models import Room

def parse_architect_input(data):
    rooms = []
    room_lookup = {}

    # ---- Create Room objects ----
    for r in data.get("rooms", []):
        room = Room(
            name=r["name"],
            area=r.get("area", 0),
            zone=r.get("zone"),
            attributes=set(r.get("attributes", []))
        )
        rooms.append(room)
        room_lookup[r["name"]] = room

    # ---- Room adjacency (Room ↔ Room) ----
    adjacency = []
    for a, b in data.get("adjacency", []):
        if a in room_lookup and b in room_lookup:
            adjacency.append((room_lookup[a], room_lookup[b]))

    # ---- Flow paths (already structured) ----
    flows = []
    for f in data.get("flows", []):
        flows.append({
            "entity": f["entity"],
            "origin": f["origin"],
            "destination": f["destination"]
        })

    return rooms, adjacency, flows
