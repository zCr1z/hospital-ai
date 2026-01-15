# backend/app.py

from engine import run_engine

def get_user_layout():
    """
    CLI-based input for Phase-1 testing.
    Frontend will later send the same structure as JSON.
    """

    rooms = []

    print("\n--- HOSPITAL LAYOUT INPUT ---")
    n = int(input("Enter number of rooms: "))

    for i in range(n):
        print(f"\nRoom {i+1}")
        room_id = input("Room ID: ").strip()
        area = float(input("Area (sqm): "))
        zone = input("Zone: ").strip()

        attributes = input(
            "Attributes (comma separated): "
        ).split(",")

        adjacent = input(
            "Adjacent rooms (comma separated room IDs): "
        ).split(",")

        rooms.append({
            "id": room_id,
            "area": area,
            "zone": zone,
            "attributes": [a.strip() for a in attributes if a.strip()],
            "adjacent_to": [a.strip() for a in adjacent if a.strip()]
        })

        # UX SAFETY
        if not rooms[-1]["attributes"]:
            print("⚠️  Warning: No attributes provided. Some rules may not apply.")

    flows = []
    add_flow = input("\nAdd patient flow? (y/n): ").lower()

    if add_flow == "y":
        path = input(
            "Flow path (comma separated room IDs): "
        ).split(",")

        flows.append({
            "entity": "Patient",
            "path": [p.strip() for p in path if p.strip()]
        })

    return {
        "rooms": rooms,
        "flows": flows
    }


# -------------------------------------------------
# MAIN
# -------------------------------------------------
if __name__ == "__main__":
    layout = get_user_layout()

    # Run compliance engine
    output = run_engine(layout)

    print("\n==============================")
    print("   COMPLIANCE ENGINE OUTPUT")
    print("==============================\n")

    # ---------------- PROCESSING LOG ----------------
    print("---- PROCESSING LOG ----")
    for log in output["logs"]:
        print(
            f"[{log['step']}] {log['status']} - {log['message']}"
        )

    # ---------------- COMPLIANCE REPORT ----------------
    print("\n---- COMPLIANCE REPORT ----")

    if not output["compliance_report"]:
        print("[INFO] SYSTEM | No applicable compliance rules triggered.")
        print("Reason: Rooms lack regulatory attributes or conflicts.")
    else:
        for r in output["compliance_report"]:
            print(
                f"[{r['severity']}] "
                f"{r['category']} | {r['rule_id']} | "
                f"{r['message']} ({r['source']})"
            )
