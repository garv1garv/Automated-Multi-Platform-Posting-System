import httpx
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult
from app.config import settings

class TelegramPlatform(BasePlatform):
    @property
    def name(self) -> str:
        return "Telegram"

    async def post(self, message: str) -> PlatformResult:
        bot_token = settings.TELEGRAM_BOT_TOKEN
        chat_id = settings.TELEGRAM_CHAT_ID

        if not bot_token or not chat_id:
            return PlatformResult(
                platform=self.name,
                status="failed",
                posted_url=None,
                public_access=False,
                date=None,
                time=None,
                error="Authentication / Configuration missing: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not provided"
            )

        api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": False
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(api_url, json=payload)
                data = response.json()

            date_str, time_str = self.get_current_datetime()

            if response.status_code == 200 and data.get("ok"):
                message_id = data.get("result", {}).get("message_id")
                # If channel username is public (e.g. @channel or channel name)
                clean_chat = chat_id.lstrip("@")
                if chat_id.startswith("@"):
                    posted_url = f"https://t.me/{clean_chat}/{message_id}"
                    public_access = True
                else:
                    posted_url = f"https://t.me/c/{clean_chat}/{message_id}"
                    public_access = False

                return PlatformResult(
                    platform=self.name,
                    status="success",
                    posted_url=posted_url,
                    public_access=public_access,
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
                    error=f"Telegram API Error ({response.status_code}): {data.get('description', response.text)}"
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

