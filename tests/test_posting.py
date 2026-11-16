import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.schemas import PlatformResult
from app.platforms.base import BasePlatform
from app.services.posting_service import PostingService

class MockSuccessPlatform(BasePlatform):
    @property
    def name(self) -> str:
        return "MockPlatformSuccess"

    async def post(self, message: str) -> PlatformResult:
        date_str, time_str = self.get_current_datetime()
        return PlatformResult(
            platform=self.name,
            status="success",
            posted_url="https://example.com/post/1001",
            public_access=True,
            date=date_str,
            time=time_str,
            error=None
        )

class MockFailingPlatform(BasePlatform):
    @property
    def name(self) -> str:
        return "MockPlatformFailure"

    async def post(self, message: str) -> PlatformResult:
        date_str, time_str = self.get_current_datetime()
        return PlatformResult(
            platform=self.name,
            status="failed",
            posted_url=None,
            public_access=False,
            date=date_str,
            time=time_str,
            error="API rate limit exceeded"
        )

@pytest.mark.asyncio
async def test_posting_service_isolation():
    service = PostingService(platforms=[MockSuccessPlatform(), MockFailingPlatform()])
    response = await service.publish_all("Hello https://example.com")

    assert response.success is True
    assert len(response.results) == 2
    success_res = next(r for r in response.results if r.platform == "MockPlatformSuccess")
    fail_res = next(r for r in response.results if r.platform == "MockPlatformFailure")

    assert success_res.status == "success"
    assert success_res.posted_url == "https://example.com/post/1001"
    assert success_res.public_access is True
    assert success_res.error is None

    assert fail_res.status == "failed"
    assert fail_res.posted_url is None
    assert fail_res.error == "API rate limit exceeded"

@pytest.mark.asyncio
async def test_endpoint_validation_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "Check out our latest business platform. https://example.com"
        }
        res = await client.post("/posting", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "success" in data
        assert "results" in data
        assert len(data["results"]) == 5

@pytest.mark.asyncio
async def test_endpoint_validation_error_over_200_chars():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "x" * 190 + " https://example.com"
        }
        res = await client.post("/posting", json=payload)
        assert res.status_code == 422
        data = res.json()
        assert data["success"] is False
        assert "Validation Error" in data["error"]

@pytest.mark.asyncio
async def test_endpoint_validation_error_missing_url():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "Check out our latest business platform with no link"
        }
        res = await client.post("/posting", json=payload)
        assert res.status_code == 422
        data = res.json()
        assert data["success"] is False
        assert any("CTA link" in d for d in data["details"])

