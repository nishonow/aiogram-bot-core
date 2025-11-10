from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from config import ADMINS
from core.db import get_admins

class AdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = data.get('event_from_user')
        if not user:
            return await handler(event, data)

        admins = await get_admins()
        if user.id in ADMINS or user.id in admins:
            return await handler(event, data)
        return
