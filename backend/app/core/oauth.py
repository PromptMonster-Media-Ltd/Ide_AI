"""
oauth.py — OAuth2 provider configuration and code exchange helpers.
Uses httpx for HTTP requests to OAuth providers.
"""
from urllib.parse import urlencode

import httpx

from app.core.config import settings

PROVIDERS = {
    "google": {
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "client_id_key": "GOOGLE_CLIENT_ID",
        "client_secret_key": "GOOGLE_CLIENT_SECRET",
        "scopes": "openid email profile",
    },
    "microsoft": {
        "auth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "userinfo_url": "https://graph.microsoft.com/v1.0/me",
        "client_id_key": "MICROSOFT_CLIENT_ID",
        "client_secret_key": "MICROSOFT_CLIENT_SECRET",
        "scopes": "openid email profile User.Read",
    },
    "github": {
        "auth_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "userinfo_url": "https://api.github.com/user",
        "client_id_key": "GITHUB_CLIENT_ID",
        "client_secret_key": "GITHUB_CLIENT_SECRET",
        "scopes": "read:user user:email",
    },
}


def get_auth_url(provider: str, redirect_uri: str) -> str:
    """Build the OAuth authorize URL for a given provider.

    Args:
        provider: One of 'google', 'microsoft', 'github'.
        redirect_uri: The callback URL the provider will redirect to after auth.

    Returns:
        The full authorization URL the frontend should redirect the user to.

    Raises:
        ValueError: If the provider is not supported or not configured.
    """
    cfg = PROVIDERS.get(provider)
    if not cfg:
        raise ValueError(f"Unsupported OAuth provider: {provider}")

    client_id = getattr(settings, cfg["client_id_key"], "")
    if not client_id:
        raise ValueError(f"OAuth provider '{provider}' is not configured (missing {cfg['client_id_key']})")

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": cfg["scopes"],
        "response_type": "code",
    }

    # Microsoft requires response_mode=query
    if provider == "microsoft":
        params["response_mode"] = "query"

    return f"{cfg['auth_url']}?{urlencode(params)}"


async def exchange_code(provider: str, code: str, redirect_uri: str) -> str:
    """Exchange an authorization code for an access token.

    Args:
        provider: One of 'google', 'microsoft', 'github'.
        code: The authorization code from the OAuth callback.
        redirect_uri: Must match the redirect_uri used in the authorize request.

    Returns:
        The access token string.

    Raises:
        ValueError: If the provider is unsupported or the exchange fails.
    """
    cfg = PROVIDERS.get(provider)
    if not cfg:
        raise ValueError(f"Unsupported OAuth provider: {provider}")

    client_id = getattr(settings, cfg["client_id_key"], "")
    client_secret = getattr(settings, cfg["client_secret_key"], "")

    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }

    headers = {"Accept": "application/json"}

    async with httpx.AsyncClient() as http:
        resp = await http.post(cfg["token_url"], data=data, headers=headers)
        resp.raise_for_status()
        body = resp.json()

    token = body.get("access_token")
    if not token:
        raise ValueError(f"OAuth token exchange failed for {provider}: {body}")

    return token


async def get_user_info(provider: str, access_token: str) -> dict:
    """Fetch the user's profile from the OAuth provider.

    Returns a normalised dict with keys: email, name, avatar_url, oauth_id.

    For GitHub, makes an additional request to /user/emails to get the
    primary email since it is not included in the main profile endpoint.
    """
    cfg = PROVIDERS.get(provider)
    if not cfg:
        raise ValueError(f"Unsupported OAuth provider: {provider}")

    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

    async with httpx.AsyncClient() as http:
        resp = await http.get(cfg["userinfo_url"], headers=headers)
        resp.raise_for_status()
        data = resp.json()

        if provider == "google":
            return {
                "email": data.get("email", ""),
                "name": data.get("name", ""),
                "avatar_url": data.get("picture", ""),
                "oauth_id": str(data.get("id", "")),
            }

        if provider == "microsoft":
            return {
                "email": data.get("mail") or data.get("userPrincipalName", ""),
                "name": data.get("displayName", ""),
                "avatar_url": "",
                "oauth_id": str(data.get("id", "")),
            }

        if provider == "github":
            email = data.get("email") or ""

            # GitHub may not include email in profile; fetch from /user/emails
            if not email:
                email_resp = await http.get(
                    "https://api.github.com/user/emails", headers=headers
                )
                if email_resp.status_code == 200:
                    emails = email_resp.json()
                    primary = next(
                        (e for e in emails if e.get("primary") and e.get("verified")),
                        None,
                    )
                    if primary:
                        email = primary["email"]
                    elif emails:
                        email = emails[0].get("email", "")

            return {
                "email": email,
                "name": data.get("name") or data.get("login", ""),
                "avatar_url": data.get("avatar_url", ""),
                "oauth_id": str(data.get("id", "")),
            }

    raise ValueError(f"Unsupported OAuth provider: {provider}")
