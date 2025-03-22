import json
from typing import List, Optional

import requests
from fastapi import HTTPException
from src.config.settings import settings

from .models import IntegrationItem
from .oauth import OAuthService


class NotionService(OAuthService):
    service_name = "notion"

    def __init__(self):
        auth_url = (
            f"{settings.notion_auth_url}?client_id={settings.notion_client_id}"
            f"&redirect_uri={settings.notion_redirect_uri}&response_type=code&owner=user"
        )
        super().__init__(
            client_id=settings.notion_client_id,
            client_secret=settings.notion_client_secret,
            redirect_uri=settings.notion_redirect_uri,
            auth_url=auth_url,
            token_url=settings.notion_token_url,
            scopes=settings.notion_scopes,
            redis_expiry=settings.redis_expiry,
            use_pkce=False,
            token_content_type="application/json",
        )

    def _recursive_dict_search(self, data: dict, target_key: str) -> Optional[str]:
        if target_key in data:
            return data[target_key]
        for value in data.values():
            if isinstance(value, dict):
                result = self._recursive_dict_search(value, target_key)
                if result is not None:
                    return result
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        result = self._recursive_dict_search(item, target_key)
                        if result is not None:
                            return result
        return None

    def create_integration_item(self, response_json: dict) -> IntegrationItem:
        name = (
            self._recursive_dict_search(response_json.get("properties", {}), "content")
            or response_json["object"] + " multi_select"
        )
        parent_type = response_json.get("parent", {}).get("type", "")
        parent_id = (
            None
            if parent_type == "workspace"
            else response_json["parent"].get(parent_type)
        )
        return IntegrationItem(
            id=response_json.get("id", ""),
            type=response_json.get("object", ""),
            name=name,
            creation_time=response_json.get("created_time", ""),
            last_modified_time=response_json.get("last_edited_time", ""),
            parent_id=parent_id,
        )

    async def get_items(self, credentials: str) -> List[IntegrationItem]:
        credentials_dict = json.loads(credentials)
        response = requests.post(
            "https://api.notion.com/v1/search",
            headers={
                "Authorization": f"Bearer {credentials_dict.get('access_token')}",
                "Notion-Version": "2022-06-28",
            },
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        results = response.json().get("results", [])
        return [self.create_integration_item(result) for result in results]


notion_service = NotionService()
