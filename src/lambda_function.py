import logging
import os

from energy_bills.controllers.customers import Customers
from energy_bills.controllers.usages import Usages

logging.basicConfig(level=logging.INFO)


def lambda_handler(event, context):
    job = os.getenv("JOB")

    if job == "invoices":
        Usages.load()
    elif job == "customers":
        Customers.load()
    else:
        logging.error("Job does not exist")

    return {
        "statusCode": 200,
        "body": "OK"
    }
