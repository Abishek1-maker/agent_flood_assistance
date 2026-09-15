import json

def get_ward_data_from_db(ward_id: int):
    """
    Returns structured data for a given ward ID.
    """
    mock_database = {
        4: {
            "ward_info": {
                "ward_name": "Ward No. 4, Kavre",
                "location_type": "Hilly terrain / Steep slopes",
                "emergency_helpline": "+977-11-440123"
            },
            "risk_metrics": {
                "landslide_risk_score": 88.5,
                "flood_risk_score": 25.0,
                "soil_type": "Clay",
                "slope_degree": 38,
                "safe_buffer_distance_meters": 150,
                "active_hazards": "Active slope displacement near market road."
            },
            "safe_zones_and_shelters": [
                {
                    "name": "Kavre Ward 4 Secondary School Compound",
                    "capacity": "250 people",
                    "status": "OPEN",
                    "elevation": "High / Stable ground",
                    "distance_from_market": "600 meters north"
                }
            ],
            "critical_services": {
                "medical_aid": "Ward Health Post (Open 24/7)",
                "open_roads": "Upper ridge road is OPEN. Main market road is CLOSED.",
                "relief_distribution": "Food/water packets available at Ward Office."
            },
            "safety_protocols": [
                "Move away from steep slopes immediately during continuous rainfall.",
                "Do not attempt to clear debris without local emergency authorities."
            ]
        },
        5: {
            "ward_info": {
                "ward_name": "Ward No. 5, Kavre",
                "location_type": "River basin / Valley floor",
                "emergency_helpline": "+977-11-440555"
            },
            "risk_metrics": {
                "landslide_risk_score": 12.0,
                "flood_risk_score": 85.0,
                "soil_type": "Sandy alluvial",
                "slope_degree": 6,
                "safe_buffer_distance_meters": 200,
                "active_hazards": "River bank overflowing near the central bridge."
            },
            "safe_zones_and_shelters": [
                {
                    "name": "Ward 5 Community Health Post (Upper Elevation)",
                    "capacity": "300 people",
                    "status": "OPEN",
                    "elevation": "High ground above flood line",
                    "distance_from_river": "450 meters uphill"
                }
            ],
            "critical_services": {
                "medical_aid": "Red Cross Emergency Tent setup near Ganesh School.",
                "open_roads": "Bridge crossing is CLOSED. North bypass highway is OPEN.",
                "relief_distribution": "Dry rations available at Health Post."
            },
            "safety_protocols": [
                "Maintain at least 200 meters distance from the riverbank.",
                "Do not cross flooded bridges on foot or motorbikes."
            ]
        }
    }
    return mock_database.get(ward_id, None)