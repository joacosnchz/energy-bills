import os
from datetime import datetime, timedelta


class Util:

    @classmethod
    def compute_daily_interval_end(cls) -> datetime:
        default_ts = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        interval_end = datetime.strptime(os.getenv("RUN_TS", default_ts), "%Y-%m-%d")

        return interval_end
    
    @classmethod
    def compute_monthly_interval_start(cls, interval_end: datetime) -> datetime:
        ts_day = int(interval_end.strftime("%d").replace("0", ""))
        last_day_previous_month = interval_end.replace(day=1) - timedelta(days=1)
        same_day_previous_month = last_day_previous_month.replace(day=ts_day)
        interval_start = same_day_previous_month + timedelta(days=1)

        return interval_start