# backend/engine.py

from pathlib import Path
from models import Room
from rule_engine import (
    load_csv,
    evaluate_area,
    evaluate_adjacency,
    evaluate_zone,
    evaluate_flow,
    evaluate_conflicts
)


def run_engine(layout, rules_folder_name="rules"):
    """
    Central orchestration layer.
    Path-safe and OS-independent.
    """

    logs = []
    results = []

    # ---------------------------------
    # 1. BUILD ROOM OBJECTS
    # ---------------------------------
    rooms = []
    for r in layout["rooms"]:
        rooms.append(
            Room(
                room_id=r["id"],
                area=r["area"],
                zone=r["zone"],
                attributes=r["attributes"],
                adjacent_to=r["adjacent_to"]
            )
        )

    # ---------------------------------
    # 2. RESOLVE RULES PATH (FIX)
    # ---------------------------------
    BASE_DIR = Path(__file__).resolve().parent   # backend/
    RULES_DIR = BASE_DIR / rules_folder_name     # backend/rules/

    if not RULES_DIR.exists():
        raise FileNotFoundError(f"Rules directory not found: {RULES_DIR}")

    # ---------------------------------
    # 3. EXECUTION PIPELINE
    # ---------------------------------

    results += evaluate_area(
        rooms,
        load_csv(RULES_DIR / "area_rules.csv"),
        logs
    )

    results += evaluate_zone(
        rooms,
        load_csv(RULES_DIR / "zone_rules.csv"),
        logs
    )

    results += evaluate_adjacency(
        rooms,
        load_csv(RULES_DIR / "adjacency_rules.csv"),
        logs
    )

    results += evaluate_flow(
        layout,
        load_csv(RULES_DIR / "flow_rules.csv"),
        logs
    )

    results += evaluate_conflicts(
        rooms,
        load_csv(RULES_DIR / "conflict_rules.csv"),
        logs
    )

    # ---------------------------------
    # 4. RETURN STRUCTURED OUTPUT
    # ---------------------------------
    return {
        "logs": [l.to_dict() for l in logs],
        "compliance_report": [r.to_dict() for r in results]
    }
