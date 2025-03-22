import json
from typing import List

import requests
from fastapi import HTTPException
from src.config.settings import settings

from .models import IntegrationItem
from .oauth import OAuthService


class HubspotService(OAuthService):
    service_name = "hubspot"

    def __init__(self):
        auth_url = (
            f"{settings.hubspot_auth_url}?client_id={settings.hubspot_client_id}"
            f"&redirect_uri={settings.hubspot_redirect_uri}&response_type=code"
        )
        super().__init__(
            client_id=settings.hubspot_client_id,
            client_secret=settings.hubspot_client_secret,
            redirect_uri=settings.hubspot_redirect_uri,
            auth_url=auth_url,
            token_url=settings.hubspot_token_url,
            scopes=settings.hubspot_scopes,
            redis_expiry=settings.redis_expiry,
            use_pkce=True,
            token_content_type="application/x-www-form-urlencoded",
        )

    def create_integration_item(self, response_json: dict) -> IntegrationItem:
        properties = response_json.get("properties", {})
        return IntegrationItem(
            id=response_json.get("id", ""),
            name=f"{properties.get('firstname', '')} {properties.get('lastname', '')}".strip(),
            email=properties.get("email", ""),
            creation_time=response_json.get("createdAt", ""),
            last_modified_time=response_json.get("lastmodifieddate", ""),
        )

    async def get_items(self, credentials: str) -> List[IntegrationItem]:
        credentials_dict = json.loads(credentials)
        access_token = credentials_dict.get("access_token")
        url = "https://api.hubapi.com/crm/v3/objects/contacts"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"limit": 100, "properties": "firstname,lastname,emaixl"}
        items = []
        after = None
        while True:
            if after:
                params["after"] = after
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, detail=response.text
                )
            data = response.json()
            for contact in data.get("results", []):
                items.append(self.create_integration_item(contact))
            after = data.get("paging", {}).get("next", {}).get("after")
            if not after:
                break
        return items


hubspot_service = HubspotService()
