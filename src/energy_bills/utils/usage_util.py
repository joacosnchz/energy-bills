import time
from datetime import datetime
from energy_bills.models.customer import Customer
from energy_bills.integrations.emporia import Emporia


class UsageUtil:

    @classmethod
    def compute_customer_usage(cls, customer: Customer, devices: list, start: datetime, end: datetime) -> float:
        """Computes total kWh energy usage from a customer"""

        emporia = Emporia()
        total_usage = 0.0
        device_ids = [d["deviceGid"] for d in devices]

        for device_id in customer.get_device_list(device_ids):
            channels = cls.get_device_channels(device_id, devices)

            for channel_id in channels:
                time.sleep(0.5)  # Sleeps a bit to avoid throttle
                device_channel_usage = emporia.get_historical_usage(
                    device=device_id,
                    channel=channel_id,
                    start=start.strftime("%Y-%m-%d"),
                    end=end.strftime("%Y-%m-%d"),
                    scale="DAY",
                    unit="KilowattHours",
                )
                total_usage += cls.sum_usage(device_channel_usage)

        return total_usage

    @classmethod
    def get_device_channels(cls, device_id: int, devices: list) -> list:
        channels = []

        for d in devices:
            if d["deviceGid"] == device_id:
                channels = d["channels"].split(",")

        return channels

    @classmethod
    def sum_usage(cls, data: list) -> float:
        usage_sum = 0.0

        if data and "usage" in data:
            for unit in data["usage"]:
                usage_sum += float(unit)

        return usage_sum