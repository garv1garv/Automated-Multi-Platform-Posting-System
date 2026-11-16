import httpx
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult
from app.config import settings

class DiscordPlatform(BasePlatform):
    @property
    def name(self) -> str:
        return "Discord"

    async def post(self, message: str) -> PlatformResult:
        webhook_url = settings.DISCORD_WEBHOOK_URL

        if not webhook_url:
            return PlatformResult(
                platform=self.name,
                status="failed",
                posted_url=None,
                public_access=False,
                date=None,
                time=None,
                error="Configuration missing: DISCORD_WEBHOOK_URL not provided"
            )

        # Discord webhooks support ?wait=true to return the created message object
        delimiter = "&" if "?" in webhook_url else "?"
        url_with_wait = f"{webhook_url}{delimiter}wait=true"

        payload = {
            "content": message
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url_with_wait, json=payload)

            date_str, time_str = self.get_current_datetime()

            if response.status_code in (200, 204):
                message_id = None
                channel_id = None
                guild_id = None
                if response.status_code == 200:
                    try:
                        data = response.json()
                        message_id = data.get("id")
                        channel_id = data.get("channel_id")
                        guild_id = data.get("guild_id")
                    except Exception:
                        pass

                if channel_id and message_id:
                    # Discord jump link format
                    g_id = guild_id if guild_id else "@me"
                    posted_url = f"https://discord.com/channels/{g_id}/{channel_id}/{message_id}"
                else:
                    # Fallback to sanitized webhook endpoint link
                    posted_url = webhook_url.split("?")[0]

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
                    error=f"Discord API Error ({response.status_code}): {response.text}"
                )

        except Exception as e:
            date_str, time_str = self.get_current_datetime()
            return PlatformResult(
                platform=self.name,
                status="failed",
                posted_url=None,
                public_access=False,
                date=date_str,
                time=time_str,
                error=f"Request failed: {str(e)}"
            )

