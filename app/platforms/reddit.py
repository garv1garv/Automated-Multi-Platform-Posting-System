import httpx
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult
from app.config import settings

class RedditPlatform(BasePlatform):
    @property
    def name(self) -> str:
        return "Reddit"

    async def post(self, message: str) -> PlatformResult:
        client_id = settings.REDDIT_CLIENT_ID
        client_secret = settings.REDDIT_CLIENT_SECRET
        username = settings.REDDIT_USERNAME
        password = settings.REDDIT_PASSWORD
        subreddit = settings.REDDIT_SUBREDDIT or "test"

        if not all([client_id, client_secret, username, password]):
            return PlatformResult(
                platform=self.name,
                status="failed",
                posted_url=None,
                public_access=False,
                date=None,
                time=None,
                error="Authentication missing: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, or REDDIT_PASSWORD not provided"
            )

        token_url = "https://www.reddit.com/api/v1/access_token"
        user_agent = f"AutomatedPoster/1.0 (by /u/{username})"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 1. Obtain OAuth Token via Password Grant
                auth = (client_id, client_secret)
                token_data = {
                    "grant_type": "password",
                    "username": username,
                    "password": password
                }
                token_resp = await client.post(
                    token_url,
                    data=token_data,
                    auth=auth,
                    headers={"User-Agent": user_agent}
                )

                if token_resp.status_code != 200:
                    date_str, time_str = self.get_current_datetime()
                    return PlatformResult(
                        platform=self.name,
                        status="failed",
                        posted_url=None,
                        public_access=False,
                        date=date_str,
                        time=time_str,
                        error=f"Reddit Auth Failed ({token_resp.status_code}): {token_resp.text}"
                    )

                access_token = token_resp.json().get("access_token")
                if not access_token:
                    date_str, time_str = self.get_current_datetime()
                    return PlatformResult(
                        platform=self.name,
                        status="failed",
                        posted_url=None,
                        public_access=False,
                        date=date_str,
                        time=time_str,
                        error=f"Reddit Auth Failed: No access token in response ({token_resp.text})"
                    )

                # 2. Submit post to subreddit
                submit_url = "https://oauth.reddit.com/api/submit"
                headers = {
                    "Authorization": f"bearer {access_token}",
                    "User-Agent": user_agent
                }

                # Title can be first 50 chars or fixed, body is message
                title = message[:50] + ("..." if len(message) > 50 else "")
                submit_data = {
                    "sr": subreddit,
                    "kind": "self",
                    "title": title,
                    "text": message
                }

                post_resp = await client.post(submit_url, data=submit_data, headers=headers)
                data = post_resp.json()

            date_str, time_str = self.get_current_datetime()

            if post_resp.status_code == 200 and data.get("success"):
                post_url = data.get("jquery", [])
                # Or from response data url:
                post_data_url = data.get("json", {}).get("data", {}).get("url")
                if not post_data_url:
                    post_data_url = f"https://reddit.com/r/{subreddit}"

                return PlatformResult(
                    platform=self.name,
                    status="success",
                    posted_url=post_data_url,
                    public_access=True,
                    date=date_str,
                    time=time_str,
                    error=None
                )
            else:
                err_msg = str(data.get("json", {}).get("errors", data))
                return PlatformResult(
                    platform=self.name,
                    status="failed",
                    posted_url=None,
                    public_access=False,
                    date=date_str,
                    time=time_str,
                    error=f"Reddit Submit Failed: {err_msg}"
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

