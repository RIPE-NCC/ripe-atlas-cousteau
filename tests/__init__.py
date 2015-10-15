definitions_schema = {
    "type": "object",
    "required": ["type", "af", "description"],
    "properties": {
        "type": {
            "type": "string",
            "enum": ["ping", "traceroute", "dns", "sslcert"]
        },
        "af": {
            "type": "integer",
            "enum": [4, 6]
        },
        "description": {
            "type": "string",
        },
        "target": {
            "type": "string",
        },
        "is_oneoff": {
            "type": "boolean",
        },
        "interval": {
            "type": "integer",
        },
    }
}
probes_create_schema = {
    "type": "object",
    "required": ["requested", "type", "value"],
    "properties": {
        "requested": {
            "type": "integer",
        },
        "type": {
            "type": "string",
            "enum": [
                "area", "country", "prefix", "asn", "probes", "msm"
            ]
        },
        "value": {
            "type": "string",
        },
        "tags": {
            "type": "object",
            "required": ["include", "exclude"],
            "properties": {
                "include": {
                    "type": "array",
                    "items": { "type": "string" }
                },
                "exclude": {
                    "type": "array",
                    "items": { "type": "string" }
                }
            }
        }
    }
}
post_data_create_schema = {
    "type": "object",
    "required": ["definitions", "probes"],
    "properties": {
        "definitions": {
            "type": "array",
            "items": definitions_schema
        },
        "start_time": {"type": "integer"},
        "end_time": {"type": "integer"},
        "is_oneoff": {"type": "boolean"},
        "probes": {
            "type": "array",
            "items": probes_create_schema
        }
    }
}

probes_change_schema = {
    "type": "object",
    "required": ["requested", "type", "value", "action"],
    "properties": {
        "requested": {
            "type": "integer",
        },
        "type": {
            "type": "string",
            "enum": ["area", "country", "prefix", "asn", "probes", "msm"]
        },
        "value": {
            "type": "string",
        },
        "action": {
            "type": "string",
            "enum": ["add", "remove"]
        },
    }
}

post_data_change_schema = {
    "type": "array",
    "items": probes_change_schema
}

__all__ = [
    "definitions_schema",
    "probes_create_schema",
    "probes_change_schema",
    "post_data_create_schema",
    "post_data_change_schema"
]
