import logging
from datetime import datetime, timedelta
from typing import Optional

from remnawave import RemnawaveSDK
from remnawave.models import CreateUserRequestDto
from remnawave.exceptions import NotFoundError

logger = logging.getLogger(__name__)


class RemnawaveService:
    def __init__(self, sdk: RemnawaveSDK, default_squad_name: str = "Default Squad"):
        self.sdk = sdk
        self.default_squad_name = default_squad_name
        self._default_squad_uuid: Optional[str] = None
    
    async def _get_default_squad_uuid(self) -> Optional[str]:
        if self._default_squad_uuid is not None:
            return self._default_squad_uuid
        
        try:
            response = await self.sdk.internal_squads.get_internal_squads()
            for squad in response.internal_squads:
                if squad.name.lower() == self.default_squad_name.lower():
                    self._default_squad_uuid = str(squad.uuid)
                    logger.info(f"Found default squad: {squad.name} ({self._default_squad_uuid})")
                    return self._default_squad_uuid
        except Exception as e:
            logger.warning(f"Could not fetch squads: {e}")
        
        return None
    
    async def get_or_create_user(self, telegram_id: int) -> str:
        username = f"tg_{telegram_id}"
        
        try:
            response = await self.sdk.users.get_user_by_username(username)
            return response.short_uuid
        except NotFoundError:
            default_squad_uuid = await self._get_default_squad_uuid()
            
            create_request = CreateUserRequestDto(
                username=username,
                expire_at=datetime.utcnow() + timedelta(days=365),
                active_internal_squads=[default_squad_uuid] if default_squad_uuid else None
            )
            response = await self.sdk.users.create_user(body=create_request)
            return response.short_uuid
    
    async def get_subscription_url(self, short_uuid: str) -> str:
        response = await self.sdk.subscriptions.get_subscription_by_short_uuid(short_uuid)
        return response.subscription_url
    
    async def add_user_to_default_squad(self, short_uuid: str) -> bool:
        squad_uuid = await self._get_default_squad_uuid()
        if not squad_uuid:
            return False
        
        try:
            user_response = await self.sdk.users.get_user_by_short_uuid(short_uuid)
            await self.sdk.internal_squads.add_users_to_internal_squad(
                uuid=squad_uuid,
                body={"user_uuids": [user_response.uuid]}
            )
            return True
        except Exception as e:
            logger.warning(f"Could not add user to squad: {e}")
            return False