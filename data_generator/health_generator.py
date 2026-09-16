# health_generator.py

import random
import uuid
from datetime import datetime


HEALTH_EVENT_TYPES = [
    "ATM_ONLINE",
    "ATM_OFFLINE",
    "CASH_LOW",
    "CASH_REFILLED",
    "HARDWARE_ERROR",
    "NETWORK_ERROR"
]


HEALTH_WEIGHTS = [
    55,   # ATM_ONLINE
    5,    # ATM_OFFLINE
    10,   # CASH_LOW
    10,   # CASH_REFILLED
    8,    # HARDWARE_ERROR
    12    # NETWORK_ERROR
]


ERROR_CODES = {
    "HARDWARE_ERROR": [
        "CARD_READER_ERROR",
        "CASH_DISPENSER_ERROR",
        "PRINTER_ERROR",
        "SCREEN_ERROR"
    ],
    "NETWORK_ERROR": [
        "NETWORK_TIMEOUT",
        "CONNECTION_LOST",
        "BANK_SERVER_UNAVAILABLE"
    ]
}


def generate_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def generate_health_event(atm, cash_low_threshold):

    event_type = random.choices(
        HEALTH_EVENT_TYPES,
        weights=HEALTH_WEIGHTS
    )[0]

    event = {
        "event_id": generate_id("health"),
        "timestamp": datetime.now().isoformat(),
        "atm_id": atm["atm_id"],
        "location": atm["location"],
        "event_type": event_type,
        "cash_level": atm["cash_level"],
        "status": atm["status"],
        "error_code": None
    }


    # -----------------------------------------
    # ATM ONLINE
    # -----------------------------------------

    if event_type == "ATM_ONLINE":

        atm["status"] = "ONLINE"

        event["status"] = "ONLINE"


    # -----------------------------------------
    # ATM OFFLINE
    # -----------------------------------------

    elif event_type == "ATM_OFFLINE":

        atm["status"] = "OFFLINE"

        event["status"] = "OFFLINE"


    # -----------------------------------------
    # CASH LOW
    # -----------------------------------------

    elif event_type == "CASH_LOW":

        # Only generate a real CASH_LOW event
        # if the current ATM state is actually low.

        if atm["cash_level"] <= cash_low_threshold:

            event["cash_level"] = atm["cash_level"]
            event["status"] = "WARNING"

        else:

            # If cash is not actually low,
            # convert this into a normal state report.

            event["event_type"] = "ATM_ONLINE"
            event["status"] = atm["status"]


    # -----------------------------------------
    # CASH REFILLED
    # -----------------------------------------

    elif event_type == "CASH_REFILLED":

        refill_amount = random.randint(
            50000,
            100000
        )

        atm["cash_level"] += refill_amount

        event["cash_level"] = atm["cash_level"]
        event["status"] = "NORMAL"


    # -----------------------------------------
    # HARDWARE ERROR
    # -----------------------------------------

    elif event_type == "HARDWARE_ERROR":

        atm["status"] = "ERROR"

        event["status"] = "ERROR"

        event["error_code"] = random.choice(
            ERROR_CODES["HARDWARE_ERROR"]
        )


    # -----------------------------------------
    # NETWORK ERROR
    # -----------------------------------------

    elif event_type == "NETWORK_ERROR":

        atm["status"] = "OFFLINE"

        event["status"] = "ERROR"

        event["error_code"] = random.choice(
            ERROR_CODES["NETWORK_ERROR"]
        )


    event["cash_level"] = atm["cash_level"]

    return event