# apps/etl/extractors/odata_extractor.py

import requests

from requests.auth import HTTPBasicAuth
from apps.common.utils.credentials import CredentialsUtil


class ODataExtractor:
    def __init__(self, timeout=60): self.timeout = timeout
    def extract(self, url: str) -> list[dict]:

        credentials = CredentialsUtil.get_odata_credentials()

        auth = HTTPBasicAuth(
            credentials["username"],
            credentials["password"]
        )

        records = []
        current_url = url

        while current_url:

            response = requests.get(
                current_url,
                auth=auth,
                timeout=self.timeout,
                headers={
                    "Accept": "application/json"
                }
            )

            response.raise_for_status()
            data = response.json()
            page_records = data.get("value", [])
            records.extend(page_records)
            current_url = data.get("@odata.nextLink")

        return records