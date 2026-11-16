import httpx
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult
from app.config import settings

class MastodonPlatform(BasePlatform):
    @property
    def name(self) -> str:
        return "Mastodon"

    async def post(self, message: str) -> PlatformResult:
        instance_url = (settings.MASTODON_INSTANCE_URL or "https://mastodon.social").rstrip("/")
        access_token = settings.MASTODON_ACCESS_TOKEN

        if not access_token:
            return PlatformResult(
                platform=self.name,
                status="failed",
                posted_url=None,
                public_access=False,
                date=None,
                time=None,
                error="Authentication missing: MASTODON_ACCESS_TOKEN not provided"
            )

        api_url = f"{instance_url}/api/v1/statuses"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "AutomatedMultiPlatformPosting/1.0"
        }
        payload = {
            "status": message,
            "visibility": "public"
        }

        date_str, time_str = self.get_current_datetime()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(api_url, json=payload, headers=headers)
                data = response.json()

            if response.status_code in (200, 201):
                posted_url = data.get("url") or data.get("uri")
                return PlatformResult(
                    platform=self.name,
                    status="success",
                    posted_url=posted_url,
                    public_access=True,
                    date=date_str,
                    time=time_str,
                    error=None
                )
            else:
                return PlatformResult(
                    platform=self.name,
                    status="failed",
                    posted_url=None,
                    public_access=False,
                    date=date_str,
                    time=time_str,
                    error=f"Mastodon API Error ({response.status_code}): {data.get('error', response.text)}"
                )

        except Exception as e:
            return PlatformResult(
                platform=self.name,
                status="failed",
                posted_url=None,
                public_access=False,
                date=date_str,
                time=time_str,
                error=f"Request failed: {str(e)}"
            )

