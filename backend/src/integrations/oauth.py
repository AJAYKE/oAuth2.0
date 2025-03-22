import asyncio
import base64
import hashlib
import json
import secrets
from typing import Dict

import httpx
from fastapi import HTTPException, Request
from fastapi.responses import HTMLResponse
from src.utils.redis import add_key_value_redis, delete_key_redis, get_value_redis


class OAuthService:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        auth_url: str,
        token_url: str,
        scopes: str,
        redis_expiry: int = 600,
        use_pkce: bool = True,
        token_content_type: str = "application/x-www-form-urlencoded",
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = auth_url
        self.token_url = token_url
        self.scopes = scopes
        self.redis_expiry = redis_expiry
        self.use_pkce = use_pkce  # Toggle PKCE support
        self.token_content_type = token_content_type  # Form-encoded or JSON

    def _create_code_challenge(self, code_verifier: str) -> str:
        m = hashlib.sha256()
        m.update(code_verifier.encode("utf-8"))
        return base64.urlsafe_b64encode(m.digest()).decode("utf-8").replace("=", "")

    async def authorize(self, user_id: str, org_id: str) -> str:
        state_data = {
            "state": secrets.token_urlsafe(32),
            "user_id": user_id,
            "org_id": org_id,
        }
        encoded_state = encoded_state = base64.urlsafe_b64encode(
            json.dumps(state_data).encode("utf-8")
        ).decode("utf-8")

        auth_url = f"{self.auth_url}&state={encoded_state}"
        if self.use_pkce:
            code_verifier = secrets.token_urlsafe(32)
            code_challenge = self._create_code_challenge(code_verifier)
            auth_url += f"&code_challenge={code_challenge}&code_challenge_method=S256"
            await add_key_value_redis(
                f"{self.service_name}_verifier:{org_id}:{user_id}",
                code_verifier,
                expire=self.redis_expiry,
            )

        if self.scopes:
            auth_url += f"&scope={self.scopes}"

        await add_key_value_redis(
            f"{self.service_name}_state:{org_id}:{user_id}",
            json.dumps(state_data),
            expire=self.redis_expiry,
        )

        return auth_url

    async def oauth2callback(self, request: Request) -> HTMLResponse:
        if request.query_params.get("error"):

            raise HTTPException(
                status_code=400, detail=request.query_params.get("error_description")
            )

        code, code_verifier, org_id, user_id = await self._verify_state_match(request)

        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        headers = {"Content-Type": self.token_content_type}

        if self.token_content_type == "application/x-www-form-urlencoded":
            token_data.update(
                {"client_id": self.client_id, "client_secret": self.client_secret}
            )
            if self.use_pkce and code_verifier:
                token_data["code_verifier"] = code_verifier.decode("utf-8")
        else:
            headers["Authorization"] = (
                f"Basic {base64.b64encode(f'{self.client_id}:{self.client_secret}'.encode()).decode()}"
            )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data=(
                    token_data
                    if self.token_content_type == "application/x-www-form-urlencoded"
                    else None
                ),
                json=(
                    token_data
                    if self.token_content_type == "application/json"
                    else None
                ),
                headers=headers,
            )
            if response.status_code != 200:

                raise HTTPException(
                    status_code=response.status_code, detail=response.text
                )

            tokens = response.json()
            await asyncio.gather(
                delete_key_redis(f"{self.service_name}_state:{org_id}:{user_id}"),
                (
                    delete_key_redis(f"{self.service_name}_verifier:{org_id}:{user_id}")
                    if self.use_pkce
                    else asyncio.sleep(0)
                ),
            )
            await add_key_value_redis(
                f"{self.service_name}_credentials:{org_id}:{user_id}",
                json.dumps(tokens),
                expire=self.redis_expiry,
            )

        return HTMLResponse(
            content="""
            <html><script>window.close();</script></html>
        """
        )

    async def _verify_state_match(self, request: Request):
        code = request.query_params.get("code")
        encoded_state = request.query_params.get("state")
        state_data = json.loads(base64.urlsafe_b64decode(encoded_state).decode("utf-8"))
        user_id = state_data.get("user_id")
        org_id = state_data.get("org_id")
        original_state = state_data.get("state")

        saved_state, code_verifier = await asyncio.gather(
            get_value_redis(f"{self.service_name}_state:{org_id}:{user_id}"),
            (
                get_value_redis(f"{self.service_name}_verifier:{org_id}:{user_id}")
                if self.use_pkce
                else asyncio.sleep(0, result=None)
            ),
        )

        if not saved_state or original_state != json.loads(saved_state).get("state"):

            raise HTTPException(status_code=400, detail="State does not match.")

        return code, code_verifier, org_id, user_id

    async def get_credentials(self, user_id: str, org_id: str) -> Dict:
        credentials = await get_value_redis(
            f"{self.service_name}_credentials:{org_id}:{user_id}"
        )
        if not credentials:

            raise HTTPException(status_code=400, detail="No credentials found.")

        credentials_dict = json.loads(credentials)
        await delete_key_redis(f"{self.service_name}_credentials:{org_id}:{user_id}")
        return credentials_dict

    @property
    def service_name(self) -> str:
        raise NotImplementedError("Subclasses must define service_name")
