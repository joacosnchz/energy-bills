import logging
from datetime import datetime, timedelta

from energy_bills.integrations.emporia import Emporia
from energy_bills.models.customer import Customer
from energy_bills.models.usage import Usage
from energy_bills.utils.usage_util import UsageUtil
from energy_bills.utils.util import Util

logger = logging.getLogger(__name__)


class Usages:

    @classmethod
    def load(cls):
        """
        Loads into DB the kWh usage for all devices of property owners.

        This could be faster if we only load data from customer's devices,
        but if the customer was loaded into the spreadsheet some days after
        they moved in, those days would be lost. Therefore, we load the
        usage for all devices no matter if there is a customer using it
        or not.
        """

        interval_end = Util.compute_daily_interval_end()

        for customer in Customer.get_active_customers(interval_end):
            logger.info(f"Loading usages for customer: {customer.id}")

            emporia = Emporia(
                username=customer.property_owner.emporia_usr,
                password=customer.property_owner.emporia_pwd,
            )
            devices = emporia.get_devices()
            customer_devices = customer.filter_devices(devices)

            for device in customer_devices:
                interval_start = cls.compute_interval_start(device, interval_end, customer)

                device_daily_usage = UsageUtil.compute_device_channel_usage(
                    device["deviceGid"], device["channels"], interval_start, interval_end, emporia
                )

                Usage.create({
                    "usage_date": interval_end,
                    "device_id": device["deviceGid"],
                    "kwh_consumed": device_daily_usage,
                })

        logger.info(f"Usages loaded with TS {interval_end}")

    @classmethod
    def compute_interval_start(cls, device: dict, interval_end: datetime, customer: Customer) -> datetime:
        last_date = Usage.find_device_last_date(device["deviceGid"])
        if last_date:
            if last_date >= interval_end.date():
                # Interval end date was already processed
                last_date = interval_end
            else:
                # Interval end date was not processed yet
                last_date = last_date + timedelta(days=1)
        else:
            # Customer does not have any usages loaded
            last_date = customer.move_in_date

        return last_date
