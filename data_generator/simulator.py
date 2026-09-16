# simulator.py

import copy
import json
import random
import time
from threading import Lock

from atm_data import ATM_DATA, CASH_LOW_THRESHOLD
from transaction_generator import generate_transaction_event
from health_generator import generate_health_event


class ATMSimulator:

    def __init__(self):

        # Create a private copy of the ATM master data.
        # This becomes the live state of our simulation.
        self.atms = copy.deepcopy(ATM_DATA)

        # Lock protects shared ATM state.
        self.lock = Lock()


    def get_random_atm(self):

        return random.choice(self.atms)


    def generate_transaction(self):

        with self.lock:

            atm = self.get_random_atm()

            return generate_transaction_event(atm)


    def generate_health_event(self):

        with self.lock:

            atm = self.get_random_atm()

            return generate_health_event(
                atm,
                CASH_LOW_THRESHOLD
            )


    def print_event(self, stream_name, event):

        print(
            f"\n[{stream_name}]"
        )

        print(
            json.dumps(
                event,
                indent=4
            )
        )


    def run(self):

        print("=" * 60)
        print("REAL-TIME ATM SIMULATOR")
        print("=" * 60)

        print(
            f"ATMs simulated: {len(self.atms)}"
        )

        print(
            f"Cash low threshold: ₹{CASH_LOW_THRESHOLD}"
        )

        print("=" * 60)


        transaction_counter = 0
        health_counter = 0


        while True:

            # --------------------------------
            # Generate transaction event
            # --------------------------------

            transaction_event = self.generate_transaction()

            transaction_counter += 1

            self.print_event(
                "TRANSACTION",
                transaction_event
            )


            # --------------------------------
            # Generate health event
            # --------------------------------

            if transaction_counter % 2 == 0:

                health_event = self.generate_health_event()

                health_counter += 1

                self.print_event(
                    "HEALTH",
                    health_event
                )


            # --------------------------------
            # Simulation delay
            # --------------------------------

            time.sleep(1)


if __name__ == "__main__":

    simulator = ATMSimulator()

    simulator.run()