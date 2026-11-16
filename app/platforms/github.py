import httpx
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult
from app.config import settings

class GitHubPlatform(BasePlatform):
    @property
    def name(self) -> str:
        return "GitHub"

    async def post(self, message: str) -> PlatformResult:
        token = settings.GITHUB_TOKEN

        if not token:
            return PlatformResult(
                platform=self.name,
                status="failed",
                posted_url=None,
                public_access=False,
                date=None,
                time=None,
                error="Authentication missing: GITHUB_TOKEN not provided"
            )

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "AutomatedMultiPlatformPosting/1.0"
        }

        # If GITHUB_REPO is provided, we create a public issue, otherwise create a public Gist
        date_str, time_str = self.get_current_datetime()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if settings.GITHUB_REPO:
                    # Create an issue
                    url = f"https://api.github.com/repos/{settings.GITHUB_REPO}/issues"
                    title = message[:50] + ("..." if len(message) > 50 else "")
                    payload = {
                        "title": title,
                        "body": message
                    }
                    response = await client.post(url, json=payload, headers=headers)
                else:
                    # Create a public Gist
                    url = "https://api.github.com/gists"
                    payload = {
                        "description": "Automated Multi-Platform Announcement",
                        "public": True,
                        "files": {
                            "announcement.md": {
                                "content": message
                            }
                        }
                    }
                    response = await client.post(url, json=payload, headers=headers)

                data = response.json()

            if response.status_code in (200, 201):
                posted_url = data.get("html_url")
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
                    error=f"GitHub API Error ({response.status_code}): {data.get('message', response.text)}"
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

