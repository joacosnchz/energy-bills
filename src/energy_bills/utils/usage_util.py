from datetime import datetime
from energy_bills.models.customer import Customer
from energy_bills.integrations.emporia import Emporia


class UsageUtil:

    @classmethod
    def compute_device_channel_usage(
        cls, device_id: int, channels: str, start: datetime, end: datetime, emporia: Emporia
    ) -> float:
        """Computes kWh consumption of a device"""

        total_usage = 0.0
        channels = channels.split(",")

        for channel_id in channels:
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
    def sum_usage(cls, data: list) -> float:
        usage_sum = 0.0

        if data and "usage" in data:
            for unit in data["usage"]:
                usage_sum += float(unit)

        return usage_sum