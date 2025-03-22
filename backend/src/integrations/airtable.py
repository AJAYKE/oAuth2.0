import json
from typing import List, Optional

import requests
from src.config.settings import settings

from .models import IntegrationItem
from .oauth import OAuthService


class AirtableService(OAuthService):
    service_name = "airtable"

    def __init__(self):
        auth_url = (
            f"{settings.airtable_auth_url}?client_id={settings.airtable_client_id}"
            f"&redirect_uri={settings.airtable_redirect_uri}&response_type=code&owner=user"
        )
        super().__init__(
            client_id=settings.airtable_client_id,
            client_secret=settings.airtable_client_secret,
            redirect_uri=settings.airtable_redirect_uri,
            auth_url=auth_url,
            token_url=settings.airtable_token_url,
            scopes=settings.airtable_scopes,
            redis_expiry=settings.redis_expiry,
            use_pkce=True,
            token_content_type="application/x-www-form-urlencoded",
        )

    def create_integration_item(
        self,
        response_json: dict,
        item_type: str,
        parent_id: Optional[str] = None,
        parent_name: Optional[str] = None,
    ) -> IntegrationItem:
        parent_id = f"{parent_id}_Base" if parent_id else None
        return IntegrationItem(
            id=f"{response_json.get('id', '')}_{item_type}",
            name=response_json.get("name", ""),
            type=item_type,
            parent_id=parent_id,
            parent_path_or_name=parent_name,
        )

    def fetch_items(
        self,
        access_token: str,
        url: str,
        aggregated_response: List[dict],
        offset: Optional[str] = None,
    ) -> None:
        params = {"offset": offset} if offset else {}
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            results = response.json().get("bases", [])
            aggregated_response.extend(results)
            offset = response.json().get("offset")
            if offset:
                self.fetch_items(access_token, url, aggregated_response, offset)

    async def get_items(self, credentials: str) -> List[IntegrationItem]:
        credentials_dict = json.loads(credentials)
        access_token = credentials_dict.get("access_token")
        url = "https://api.airtable.com/v0/meta/bases"
        items = []
        bases = []
        self.fetch_items(access_token, url, bases)
        for base in bases:
            items.append(self.create_integration_item(base, "Base"))
            tables_response = requests.get(
                f"https://api.airtable.com/v0/meta/bases/{base.get('id')}/tables",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if tables_response.status_code == 200:
                for table in tables_response.json()["tables"]:
                    items.append(
                        self.create_integration_item(
                            table, "Table", base.get("id"), base.get("name")
                        )
                    )
        return items


airtable_service = AirtableService()
