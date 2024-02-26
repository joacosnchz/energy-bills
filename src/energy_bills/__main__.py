import logging

from energy_bills.controllers.customers import Customers

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    Customers.load()
