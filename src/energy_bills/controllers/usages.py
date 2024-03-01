import logging
from energy_bills.integrations.emporia import Emporia
from energy_bills.models.customer import Customer
from energy_bills.utils.usage_util import UsageUtil
from energy_bills.utils.util import Util
from energy_bills.models.usage import Usage

logger = logging.getLogger(__name__)


class Usages:

    @classmethod
    def load(cls):
        interval_end = Util.compute_daily_interval_end()

        emporia = Emporia()
        devices = emporia.get_devices()

        # TODO: Get only the customers that have not moved out or moved out yesterday
        for customer in Customer.get_all():
            logger.info(f"Processing customer ID: {customer.id}")
            customer_daily_usage = UsageUtil.compute_customer_usage(customer, devices, interval_end, interval_end)

            Usage.upsert({
                "usage_date": interval_end,
                "customer_id": customer.id,
                "kwh_consumed": customer_daily_usage,
            })
        
        logger.info(f"Usages loaded with TS {interval_end}")
