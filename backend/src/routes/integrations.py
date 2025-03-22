from fastapi import APIRouter, Form, HTTPException, Request
from src.integrations import AirtableService, HubspotService, NotionService

router = APIRouter()

services = {
    "hubspot": HubspotService(),
    "airtable": AirtableService(),
    "notion": NotionService(),
}


@router.post("/authorize")
async def authorize(
    integration_type: str = Form(...), user_id: str = Form(...), org_id: str = Form(...)
):
    service = services.get(integration_type.lower())
    if not service:
        raise HTTPException(status_code=400, detail="Invalid integration type")
    return await service.authorize(user_id, org_id)


@router.get("/oauth2callback")
async def oauth2callback(request: Request, integration_type: str):
    service = services.get(integration_type.lower())
    if not service:
        raise HTTPException(status_code=400, detail="Invalid integration type")
    return await service.oauth2callback(request)


@router.post("/credentials")
async def get_credentials(
    integration_type: str = Form(...), user_id: str = Form(...), org_id: str = Form(...)
):
    service = services.get(integration_type.lower())
    if not service:
        raise HTTPException(status_code=400, detail="Invalid integration type")
    return await service.get_credentials(user_id, org_id)


@router.post("/load")
async def get_items(integration_type: str = Form(...), credentials: str = Form(...)):
    service = services.get(integration_type.lower())
    if not service:
        raise HTTPException(status_code=400, detail="Invalid integration type")
    return await service.get_items(credentials)
