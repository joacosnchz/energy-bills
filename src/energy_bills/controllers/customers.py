import logging

import pandas as pd
from pandas import DataFrame

from energy_bills.integrations.google import Google
from energy_bills.models.customer import Customer
from energy_bills.models.property_owner import PropertyOwner

logger = logging.getLogger(__name__)


class Customers:

    @classmethod
    def load(cls):
        for po in PropertyOwner.get_all():
            data = Google.get_spreadsheet(
                id=po.customers_list_id,
                range="Sheet1!A3:J",
            )

            df = pd.DataFrame(data)
            df = df.drop(0)
            df.columns = [
                "pad_id", "aniversary_day", "first_name", "last_name", "phone", "email", "move_in", "move_out_day",
                "devices"
            ]
            df["property_owner_id"] = po.id

            logger.info(f"Found {len(df)} valid rows")

            for _, row in df.iterrows():
                Customer.upsert(row.to_dict())

        logger.info("Customers load function executed")
