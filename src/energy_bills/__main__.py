import logging
import os

from energy_bills.controllers.customers import Customers
from energy_bills.controllers.invoices import Invoices
from energy_bills.controllers.usages import Usages

logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    job = os.getenv("JOB")

    if job == "invoices":
        Usages.load()
        Invoices.load()
        Invoices.generate_links()
    elif job == "customers":
        Customers.load()
    else:
        logging.error("Job does not exist")
