import asyncio
from typing import List
from app.platforms import (
    BasePlatform,
    TelegramPlatform,
    DiscordPlatform,
    RedditPlatform,
    GitHubPlatform,
    MastodonPlatform,
)
from app.schemas import PlatformResult, PostMessageResponse

class PostingService:
    def __init__(self, platforms: List[BasePlatform] = None):
        if platforms is None:
            self.platforms: List[BasePlatform] = [
                TelegramPlatform(),
                DiscordPlatform(),
                RedditPlatform(),
                GitHubPlatform(),
                MastodonPlatform(),
            ]
        else:
            self.platforms = platforms

    async def _post_safe(self, platform: BasePlatform, message: str) -> PlatformResult:
        try:
            return await platform.post(message)
        except Exception as e:
            date_str, time_str = platform.get_current_datetime()
            return PlatformResult(
                platform=platform.name,
                status="failed",
                posted_url=None,
                public_access=False,
                date=date_str,
                time=time_str,
                error=f"Unhandled platform error: {str(e)}"
            )

    async def publish_all(self, message: str) -> PostMessageResponse:
        """
        Broadcast the message concurrently across all platforms.
        Ensures individual platform failures do not impact others.
        """
        tasks = [self._post_safe(platform, message) for platform in self.platforms]
        results: List[PlatformResult] = await asyncio.gather(*tasks)

        # Check if at least one platform succeeded or return overall status
        has_success = any(r.status == "success" for r in results)

        return PostMessageResponse(
            success=has_success,
            results=results
        )

