from abc import ABC, abstractmethod
from datetime import datetime, timezone
from app.schemas import PlatformResult

class BasePlatform(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the platform."""
        pass

    @abstractmethod
    async def post(self, message: str) -> PlatformResult:
        """
        Publish the given message to the platform.
        Must handle its own exceptions and always return a PlatformResult.
        """
        pass

    @staticmethod
    def get_current_datetime():
        """Returns (date_str, time_str) in UTC or local ISO format."""
        now = datetime.now()
        return now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")

