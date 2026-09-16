# transaction_generator.py

import random
import uuid
from datetime import datetime


TRANSACTION_TYPES = [
    "WITHDRAWAL",
    "DEPOSIT",
    "BALANCE_CHECK",
    "FAILED_TRANSACTION",
    "CARD_RETAINED"
]


TRANSACTION_WEIGHTS = [
    55,   # WITHDRAWAL
    15,   # DEPOSIT
    20,   # BALANCE_CHECK
    8,    # FAILED_TRANSACTION
    2     # CARD_RETAINED
]


WITHDRAWAL_AMOUNTS = [
    100,
    200,
    500,
    1000,
    2000,
    5000,
    10000
]


DEPOSIT_AMOUNTS = [
    500,
    1000,
    2000,
    5000,
    10000
]


CARD_TYPES = [
    "DEBIT",
    "CREDIT"
]


def generate_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def generate_transaction_event(atm):

    transaction_type = random.choices(
        TRANSACTION_TYPES,
        weights=TRANSACTION_WEIGHTS
    )[0]

    event = {
        "event_id": generate_id("evt"),
        "timestamp": datetime.now().isoformat(),
        "atm_id": atm["atm_id"],
        "location": atm["location"],
        "transaction_type": transaction_type,
        "transaction_id": None,
        "amount": 0,
        "card_type": None,
        "status": None
    }


    # -----------------------------------------
    # WITHDRAWAL
    # -----------------------------------------

    if transaction_type == "WITHDRAWAL":

        amount = random.choice(WITHDRAWAL_AMOUNTS)

        # ATM must have enough cash
        if atm["status"] != "ONLINE":

            event["status"] = "FAILED"
            event["transaction_id"] = generate_id("txn")

        elif atm["cash_level"] < amount:

            event["status"] = "FAILED"
            event["transaction_id"] = generate_id("txn")
            event["amount"] = amount

        else:

            atm["cash_level"] -= amount

            event["transaction_id"] = generate_id("txn")
            event["amount"] = amount
            event["card_type"] = random.choice(CARD_TYPES)
            event["status"] = "SUCCESS"


    # -----------------------------------------
    # DEPOSIT
    # -----------------------------------------

    elif transaction_type == "DEPOSIT":

        if atm["status"] != "ONLINE":

            event["status"] = "FAILED"
            event["transaction_id"] = generate_id("txn")

        else:

            amount = random.choice(DEPOSIT_AMOUNTS)

            atm["cash_level"] += amount

            event["transaction_id"] = generate_id("txn")
            event["amount"] = amount
            event["card_type"] = random.choice(CARD_TYPES)
            event["status"] = "SUCCESS"


    # -----------------------------------------
    # BALANCE CHECK
    # -----------------------------------------

    elif transaction_type == "BALANCE_CHECK":

        event["transaction_id"] = generate_id("txn")
        event["card_type"] = random.choice(CARD_TYPES)

        if atm["status"] == "ONLINE":
            event["status"] = "SUCCESS"
        else:
            event["status"] = "FAILED"


    # -----------------------------------------
    # FAILED TRANSACTION
    # -----------------------------------------

    elif transaction_type == "FAILED_TRANSACTION":

        event["transaction_id"] = generate_id("txn")
        event["amount"] = random.choice(WITHDRAWAL_AMOUNTS)
        event["card_type"] = random.choice(CARD_TYPES)
        event["status"] = "FAILED"


    # -----------------------------------------
    # CARD RETAINED
    # -----------------------------------------

    elif transaction_type == "CARD_RETAINED":

        event["transaction_id"] = generate_id("txn")
        event["card_type"] = random.choice(CARD_TYPES)
        event["status"] = "FAILED"


    return event