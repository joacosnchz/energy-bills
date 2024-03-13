import logging

from energy_bills.integrations.emporia import Emporia
from energy_bills.integrations.stripe import Stripe
from energy_bills.models.customer import Customer
from energy_bills.models.usage import Usage
from energy_bills.utils.usage_util import UsageUtil
from energy_bills.utils.util import Util
from energy_bills.models.invoice import Invoice

logger = logging.getLogger(__name__)


class Invoices:

    @classmethod
    def load(cls) -> None:
        """Generates stripe invoices based on kWh usage from customers"""

        interval_end = Util.compute_daily_interval_end()
        interval_start = Util.compute_monthly_interval_start(interval_end)

        stripe = Stripe()
        prod_id = cls.get_or_create_stripe_product()

        for customer in Customer.get_active_billable_customers(interval_end):
            logger.info(f"Generating invoices for customer ID: {customer.id} from {interval_start} to {interval_end}")

            emporia = Emporia(
                username=customer.property_owner.emporia_usr,
                password=customer.property_owner.emporia_pwd,
            )
            devices = emporia.get_devices()
            customer_devices = customer.filter_devices(devices)

            customer_monthly_usage_api = 0.0
            customer_monthly_usage_db = 0.0
            for device in customer_devices:
                device_monthly_usage_api = UsageUtil.compute_device_channel_usage(
                    device["deviceGid"], device["channels"], interval_start, interval_end, emporia
                )
                customer_monthly_usage_api += device_monthly_usage_api

                device_monthly_usage_db = Usage.compute_device_usage(
                    device["deviceGid"], interval_start, interval_end
                )
                customer_monthly_usage_db += device_monthly_usage_db

            customer_monthly_usage = max(customer_monthly_usage_api, customer_monthly_usage_db)

            invoice_amount = customer_monthly_usage * customer.property_owner.kwh_rate
            price_id = stripe.create_price(invoice_amount, prod_id)
            payment = stripe.create_payment_link(price_id, quantity=1)

            Invoice.create({
                "invoice_date": interval_end,
                "customer_id": customer.id,
                "kwh_consumed": customer_monthly_usage,
                "kwh_rate": customer.property_owner.kwh_rate,
                "amount": invoice_amount,
                "stripe_id": payment["id"],
                "link": payment["url"],
            })

        logger.info(f"Invoices load completed with TS {interval_end}")

    @classmethod
    def get_or_create_stripe_product(cls) -> str:
        stripe = Stripe()
        stripe_product_name = "Energy Service"
        prod_id = stripe.search_product(name=stripe_product_name)
        if not prod_id:
            logger.info("Stripe product does not exist, creating..")
            prod_id = stripe.create_product(name=stripe_product_name)

        return prod_id
