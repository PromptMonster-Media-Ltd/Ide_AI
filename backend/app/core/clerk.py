"""
clerk.py — Clerk JWT verification using JWKS (RS256).
Fetches and caches Clerk's public keys, then verifies incoming session tokens.
"""
import httpx
import jwt
from cachetools import TTLCache
from jwt import PyJWKClient

from app.core.config import settings

# Cache the PyJWKClient instance (refreshes keys internally)
_jwk_clients: TTLCache = TTLCache(maxsize=1, ttl=3600)

_JWK_CLIENT_KEY = "clerk"


def _get_jwk_client() -> PyJWKClient:
    """Return a cached PyJWKClient that fetches Clerk's JWKS endpoint."""
    if _JWK_CLIENT_KEY not in _jwk_clients:
        _jwk_clients[_JWK_CLIENT_KEY] = PyJWKClient(settings.CLERK_JWKS_URL)
    return _jwk_clients[_JWK_CLIENT_KEY]


def verify_clerk_token(token: str) -> dict:
    """
    Verify a Clerk session JWT.

    Returns the decoded payload with at minimum:
      - sub: Clerk user ID (e.g. "user_2x...")
      - exp, iat, nbf: timing claims

    Raises jwt.exceptions.PyJWTError on any validation failure.
    """
    client = _get_jwk_client()
    signing_key = client.get_signing_key_from_jwt(token)

    payload = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        options={
            "verify_exp": True,
            "verify_iat": True,
            "verify_nbf": True,
        },
    )

    return payload
