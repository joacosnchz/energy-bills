import logging
import os

from energy_bills.controllers.customers import Customers
from energy_bills.controllers.invoices import Invoices
from energy_bills.controllers.usages import Usages

FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt="%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    job = os.getenv("JOB")

    if job == "invoices":
        Usages.load()
        Invoices.load()
        Invoices.generate_links()
        Invoices.send_invoices()
    elif job == "customers":
        Customers.load()
    else:
        logging.error("Job does not exist")
