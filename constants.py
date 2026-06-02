# ==========================
# EVENT CATALOG
# ==========================

EVENT_CATALOG = {
    1: {
        "display": "Gift Given",
        "name": "gift_given",
        "trust_change": 5,
        "importance": 7
    },

    2: {
        "display": "Argument",
        "name": "argument",
        "trust_change": -3,
        "importance": 8
    },

    3: {
        "display": "Mission Complete",
        "name": "mission_complete",
        "trust_change": 8,
        "importance": 6
    },

    4: {
        "display": "Promise Made",
        "name": "promise_made",
        "trust_change": 3,
        "importance": 5
    },

    5: {
        "display": "Promise Broken",
        "name": "promise_broken",
        "trust_change": -10,
        "importance": 10
    },

    6: {
        "display": "Romantic Moment",
        "name": "romantic_moment",
        "trust_change": 10,
        "importance": 9
    },

    7: {
        "display": "Shared Secret",
        "name": "shared_secret",
        "trust_change": 5,
        "importance": 8
    },

    8: {
        "display": "Betrayal",
        "name": "betrayal",
        "trust_change": -15,
        "importance": 10
    },

    9: {
        "display": "Memory Extracted",
        "name": "memory_extracted",
        "trust_change": 0,
        "importance": 5
    }
}


# ==========================
# MEMORY EXTRACTION PATTERNS
# ==========================

MEMORY_PATTERNS = {

    "promise": {
        "template": "User made a promise.",
        "importance": 8
    },

    "love": {
        "template": "A romantic moment occurred.",
        "importance": 10
    },

    "secret": {
        "template": "A secret was shared.",
        "importance": 8
    },

    "gift": {
        "template": "A gift was exchanged.",
        "importance": 6
    },

    "help": {
        "template": "User offered assistance.",
        "importance": 5
    }
}