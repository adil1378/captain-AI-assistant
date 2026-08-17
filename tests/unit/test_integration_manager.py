"""
Unit & Integration Tests for Volume 10 Part 10D External Integration Architecture.
Verifies provider registration, credential encryption & masking, API request execution,
protocol adapters, and telemetry tracking.
"""

import pytest
import asyncio
from src.backend.core.integration_manager import (
    ExternalIntegrationManager,
    ProviderConfig,
    IntegrationProtocol,
    AuthMechanism,
    IntegrationRequest,
    IntegrationResponse
)


def test_credential_manager():
    manager = ExternalIntegrationManager()
    rec = manager.credential_manager.store_secret(
        credential_id="cred_openai",
        secret_data="sk-proj-1234567890abcdef",
        auth_mechanism=AuthMechanism.API_KEY
    )

    assert rec.masked_secret == "sk-p****cdef"
    assert manager.credential_manager.get_secret("cred_openai") == "sk-proj-1234567890abcdef"

    with pytest.raises(KeyError):
        manager.credential_manager.get_secret("cred_nonexistent")


@pytest.mark.anyio
async def test_provider_registration_and_execution():
    manager = ExternalIntegrationManager()

    config = ProviderConfig(
        provider_id="prov_github",
        name="GitHub REST API",
        protocol=IntegrationProtocol.REST,
        endpoint="https://api.github.com"
    )

    async def github_adapter(req: IntegrationRequest, secret: str) -> IntegrationResponse:
        assert secret == "ghp_12345678"
        return IntegrationResponse(
            request_id=req.request_id,
            status_code=200,
            data={"user": "captain-ai", "repos": 5},
            latency_ms=15.5
        )

    manager.credential_manager.store_secret("cred_github", "ghp_12345678")
    manager.register_provider(config, github_adapter)

    req = IntegrationRequest(
        request_id="req_101",
        provider_id="prov_github",
        credential_id="cred_github",
        endpoint_path="/user"
    )

    res = await manager.execute(req)
    assert res.status_code == 200
    assert res.data["user"] == "captain-ai"
    assert manager.telemetry["total_requests"] == 1


@pytest.mark.anyio
async def test_inactive_provider_rejection():
    manager = ExternalIntegrationManager()
    config = ProviderConfig(
        provider_id="prov_disabled",
        name="Disabled SaaS",
        protocol=IntegrationProtocol.REST,
        endpoint="https://api.disabled.com",
        is_active=False
    )
    manager.register_provider(config)

    req = IntegrationRequest(request_id="req_err", provider_id="prov_disabled")

    with pytest.raises(RuntimeError):
        await manager.execute(req)
