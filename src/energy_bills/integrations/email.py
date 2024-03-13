import logging
import os

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class Email:

    @classmethod
    def send(cls, subject: str, recipient: str, body: str) -> None:
        client = boto3.client("ses")

        try:
            client.send_email(
                Destination={
                    "ToAddresses": [
                        recipient,
                    ],
                },
                Message={
                    "Body": {
                        "Text": {
                            "Charset": "UTF-8",
                            "Data": body,
                        },
                    },
                    "Subject": {
                        "Charset": "UTF-8",
                        "Data": subject,
                    },
                },
                Source=os.getenv("EMAIL_SENDER"),
            )

        except ClientError as e:
            logger.error(e.response["Error"]["Message"])
