"""
JSON Schema definitions for Restful-Booker API responses.
"""

BOOKING_SCHEMA = {
    "type": "object",
    "required": [
        "firstname", "lastname", "totalprice",
        "depositpaid", "bookingdates"
    ],
    "properties": {
        "firstname":       {"type": "string"},
        "lastname":        {"type": "string"},
        "totalprice":      {"type": "integer"},
        "depositpaid":     {"type": "boolean"},
        "additionalneeds": {"type": "string"},
        "bookingdates": {
            "type": "object",
            "required": ["checkin", "checkout"],
            "properties": {
                "checkin":  {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
                "checkout": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}

CREATE_BOOKING_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["bookingid", "booking"],
    "properties": {
        "bookingid": {"type": "integer"},
        "booking":   BOOKING_SCHEMA,
    },
    "additionalProperties": False,
}