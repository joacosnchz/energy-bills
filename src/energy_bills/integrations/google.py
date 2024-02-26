import json
import logging
import os
import os.path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
logger = logging.getLogger(__name__)


class Google:

    @classmethod
    def get_spreadsheet(cls, id: str, range: str) -> list:
        creds = None

        json_data = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        json_key = json.loads(json_data, strict=False)
        creds = service_account.Credentials.from_service_account_info(
            json_key,
            scopes=SCOPES,
        )

        try:
            service = build("sheets", "v4", credentials=creds)

            sheet = service.spreadsheets()
            result = (
                sheet.values()
                .get(spreadsheetId=id, range=range)
                .execute()
            )

            return result.get("values", [])
        except HttpError as err:
            logger.error(str(err))
