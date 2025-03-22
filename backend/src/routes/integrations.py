from typing import Any, Dict

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from src.integrations import AirtableService, HubspotService, NotionService

router = APIRouter()

services: Dict[str, Any] = {
    "hubspot": HubspotService(),
    "airtable": AirtableService(),
    "notion": NotionService(),
}


async def get_service(request: Request) -> Any:
    integration_type = None
    if request.method == "GET":
        integration_type = request.query_params.get("integration_type")
    elif request.method == "POST":
        form_data = await request.form()
        integration_type = form_data.get("integration_type")

    if not integration_type:
        raise HTTPException(status_code=400, detail="Missing integration_type")

    service = services.get(integration_type.lower())
    if not service:
        raise HTTPException(status_code=400, detail="Invalid integration type")

    request.state.service = service
    return service


@router.post("/authorize")
async def authorize(
    user_id: str = Form(...),
    org_id: str = Form(...),
    service: Any = Depends(get_service),
):
    return await service.authorize(user_id, org_id)


@router.get("/oauth2callback")
async def oauth2callback(request: Request, service: Any = Depends(get_service)):
    return await service.oauth2callback(request)


@router.post("/credentials")
async def get_credentials(
    user_id: str = Form(...),
    org_id: str = Form(...),
    service: Any = Depends(get_service),
):
    return await service.get_credentials(user_id, org_id)


@router.post("/load")
async def get_items(credentials: str = Form(...), service: Any = Depends(get_service)):
    return await service.get_items(credentials)
