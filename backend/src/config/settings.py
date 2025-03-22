from pydantic import BaseSettings


class Settings(BaseSettings):
    # HubSpot
    hubspot_client_id: str
    hubspot_client_secret: str
    hubspot_redirect_uri: str = (
        "http://localhost:8000/integrations/oauth2callback?integration_type=hubspot"
    )
    hubspot_scopes: str = (
        "crm.objects.contacts.read crm.objects.contacts.write crm.schemas.deals.read crm.schemas.deals.write oauth"
    )
    hubspot_auth_url: str = "https://app.hubspot.com/oauth/authorize"
    hubspot_token_url: str = "https://api.hubapi.com/oauth/v1/token"

    # Airtable
    airtable_client_id: str
    airtable_client_secret: str
    airtable_redirect_uri: str = (
        "http://localhost:8000/integrations/oauth2callback?integration_type=airtable"
    )
    airtable_scopes: str = (
        "data.records:read data.records:write data.recordComments:read data.recordComments:write schema.bases:read schema.bases:write"
    )
    airtable_auth_url: str = "https://airtable.com/oauth2/v1/authorize"
    airtable_token_url: str = "https://airtable.com/oauth2/v1/token"

    # Notion
    notion_client_id: str
    notion_client_secret: str
    notion_redirect_uri: str = (
        "http://localhost:8000/integrations/oauth2callback?integration_type=notion"
    )
    notion_scopes: str = ""  # Notion doesn’t use scopes in the same way
    notion_auth_url: str = "https://api.notion.com/v1/oauth/authorize"
    notion_token_url: str = "https://api.notion.com/v1/oauth/token"

    redis_expiry: int = 600

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
