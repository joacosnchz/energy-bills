import logging
from energy_bills.integrations.emporia import Emporia
from energy_bills.models.property_owner import PropertyOwner
from energy_bills.utils.usage_util import UsageUtil
from energy_bills.utils.util import Util
from energy_bills.models.usage import Usage

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

        for owner in PropertyOwner.get_all():
            logger.info(f"Loading usages for Owner: {owner.id}")
            emporia = Emporia(
                username=owner.emporia_usr,
                password=owner.emporia_pwd,
            )
            devices = emporia.get_devices()

            for device in devices:
                device_daily_usage = UsageUtil.compute_device_channel_usage(
                    device["deviceGid"], device["channels"], interval_end, interval_end, emporia
                )

                Usage.upsert({
                    "usage_date": interval_end,
                    "device_id": device["deviceGid"],
                    "kwh_consumed": device_daily_usage,
                })
        
        logger.info(f"Usages loaded with TS {interval_end}")
