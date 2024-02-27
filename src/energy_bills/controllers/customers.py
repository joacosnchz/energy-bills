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
            cls.validate_number_of_columns(df)
            df = df.drop(0)
            df.columns = [
                "pad_id", "aniversary_day", "first_name", "last_name", "phone", "email", "move_in", "move_out_day",
                "devices"
            ]
            df["property_owner_id"] = po.id
            df = cls.filter_invalid_rows(df)
            df = cls.replace_empty_strings(df)
            df = cls.change_data_types(df)

            logger.info(f"Found {len(df)} valid rows")

            for _, row in df.iterrows():
                Customer.upsert(row.to_dict())

        logger.info("Customers load function executed")

    @classmethod
    def filter_invalid_rows(cls, df: DataFrame) -> DataFrame:
        # Filter nulls
        not_null_columns = ["pad_id", "aniversary_day", "first_name", "last_name", "email", "devices"]
        df = df[~df[not_null_columns].isnull().any(axis=1)]

        # Filter invalid types
        int_columns = ["pad_id", "aniversary_day"]
        for column in int_columns:
            df = df[df[column].apply(lambda x: x.isnumeric())]

        # Filter invalid nullable types
        nullable_int_columns = ["move_out_day"]
        for column in nullable_int_columns:
            df = df[df[column].apply(lambda x: not x or x.isnumeric())]

        # Validates devices column
        pattern = r"^([0-9](,)?)+$"
        df["devices_valid"] = df["devices"].str.contains(pattern, regex=True)
        df = df[df["devices_valid"]]
        df = df.drop(columns=["devices_valid"])

        return df

    @classmethod
    def replace_empty_strings(cls, df: DataFrame) -> DataFrame:
        df["move_in"] = df["move_in"].replace("", None)
        df["move_out_day"] = df["move_out_day"].replace("", None)
        df["phone"] = df["phone"].replace("", None)
        df["devices"] = df["devices"].replace("", None)

        return df

    @classmethod
    def change_data_types(cls, df: DataFrame) -> DataFrame:
        df["pad_id"] = df["pad_id"].astype(int)
        df["aniversary_day"] = df["aniversary_day"].astype(int)

        df["move_out_day"] = df["move_out_day"].astype('Int64')

        return df

    @classmethod
    def validate_number_of_columns(cls, df: DataFrame) -> None:
        expected_col_number = 9
        if df.shape[1] != expected_col_number:
            logger.error(f"Number of columns is not {expected_col_number}")
            raise Exception(f"Number of columns is not {expected_col_number}")
