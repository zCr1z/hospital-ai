import json

def parse_text_with_llm(text):
    """
    This simulates an LLM.
    In production: replace this with GPT / Gemini API.
    For hackathon: this is PERFECT and acceptable.
    """

    # ---- MOCKED LLM OUTPUT (IMPORTANT) ----
    # The LLM ONLY extracts facts, no logic.
    llm_output = """
    {
      "rooms": [
        {
          "name": "MRI Room",
          "area": 22,
          "zone": "MRI_Zone_IV",
          "attributes": ["Has_Radiation", "Is_MRI", "Imaging_Room"]
        },
        {
          "name": "CT Room",
          "area": 24,
          "zone": "Restricted_Radiation_Zone",
          "attributes": ["Has_Radiation", "Imaging_Room"]
        },
        {
          "name": "Waiting Area",
          "area": 18,
          "zone": "Public_Zone",
          "attributes": ["Public_Accessible", "Waiting_Area"]
        },
        {
          "name": "Lift Core",
          "area": 10,
          "zone": "Any_Zone",
          "attributes": ["Lift_Core", "Vibration_Source"]
        }
      ],
      "adjacency": [
        ["MRI Room", "Lift Core"],
        ["CT Room", "Waiting Area"]
      ],
      "flows": [
        {
          "entity": "Patient",
          "origin": "Public_Zone",
          "destination": "Restricted_Radiation_Zone"
        },
        {
          "entity": "Staff",
          "origin": "MRI_Zone_I",
          "destination": "MRI_Zone_IV"
        }
      ]
    }
    """

    return json.loads(llm_output)
