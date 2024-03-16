import logging
from datetime import datetime

from energy_bills.integrations.email import Email
from energy_bills.integrations.emporia import Emporia
from energy_bills.integrations.stripe import Stripe
from energy_bills.models.customer import Customer
from energy_bills.models.invoice import Invoice
from energy_bills.models.property_owner import PropertyOwner
from energy_bills.models.usage import Usage
from energy_bills.utils.usage_util import UsageUtil
from energy_bills.utils.util import Util

logger = logging.getLogger(__name__)


class Invoices:

    @classmethod
    def load(cls) -> None:
        """Generates stripe invoices based on kWh usage from customers"""

        interval_end = Util.compute_daily_interval_end()
        interval_start = Util.compute_monthly_interval_start(interval_end)

        for customer in Customer.get_active_billable_customers(interval_end):
            logger.info(f"Loading invoices for customer ID: {customer.id} from {interval_start} to {interval_end}")

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
            invoice_amount = customer_monthly_usage * customer.property_owner.kwh_rate / 100

            Invoice.create({
                "invoice_date": interval_end,
                "customer_id": customer.id,
                "kwh_consumed": customer_monthly_usage,
                "kwh_rate": customer.property_owner.kwh_rate,
                "amount": invoice_amount,
            })

        logger.info(f"Invoices load completed with TS {interval_end}")

    @classmethod
    def generate_links(cls):
        """Creates stripe payment links from loaded invoices"""

        stripe = Stripe()
        prod_id = cls.get_or_create_stripe_product()

        for invoice in Invoice.get_all_without_link():
            logger.info(f"Generating stripe invoice for ID: {invoice.id}")

            price_id = invoice.customer.property_owner.stripe_price_id
            if not price_id:
                price_id = stripe.create_price(invoice.kwh_rate, prod_id)
                PropertyOwner.update_by_id({
                    "id": invoice.customer.property_owner_id,
                    "stripe_price_id": price_id,
                })

            payment_data = stripe.create_payment_link(price_id, quantity=invoice.kwh_consumed)

            Invoice.update_by_id({
                "id": invoice.id,
                **payment_data
            })

        logger.info("Stripe invoices generated")

    @classmethod
    def send_invoices(cls):
        """Sends stripe payment link by email"""

        owners_notifications = {}

        for invoice in Invoice.get_all_not_sent():
            logger.info(f"Sending invoice ID: {invoice.id}")

            Email.send(
                subject="RV Park Billing",
                recipient=invoice.customer.email,
                body=f"""
                Hello,

                This is the invoice for the energy usage on the RV Park.
                Please use the following link for payment: {invoice.link}

                Greetings
                """
            )

            Invoice.update_by_id({
                "id": invoice.id,
                "sent_at": datetime.now(),
            })

            if invoice.customer.property_owner.email not in owners_notifications:
                owners_notifications[invoice.customer.property_owner.email] = {
                    "invoices": [invoice]
                }
            else:
                owners_notifications[invoice.customer.property_owner.email]["invoices"].append(invoice)

        for owner_email, notifications in owners_notifications.items():
            message = "Dear Property Owner, today the following invoices were sent:\n"
            for invoice in notifications["invoices"]:
                message += (
                    f"{invoice.customer.first_name} {invoice.customer.last_name} - "
                    f"Site {invoice.customer.pad_id} - Anniversary {invoice.customer.aniversary_day} - "
                    f"${invoice.amount:.0f}\n"
                )

            Email.send(
                subject="RV Park Billing",
                recipient=owner_email,
                body=message,
            )

        logger.info("Invoices sent")

    @classmethod
    def get_or_create_stripe_product(cls) -> str:
        stripe = Stripe()
        stripe_product_name = "Energy Service"
        prod_id = stripe.search_product(name=stripe_product_name)
        if not prod_id:
            logger.info("Stripe product does not exist, creating..")
            prod_id = stripe.create_product(name=stripe_product_name)

        return prod_id
