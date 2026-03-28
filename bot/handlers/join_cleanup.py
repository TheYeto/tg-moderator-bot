"""Handler that deletes 'new member joined' service messages."""

import logging

from aiogram import F, Router
from aiogram.types import Message

logger = logging.getLogger(__name__)

router = Router(name="join_cleanup")


@router.message(F.new_chat_members)
async def delete_join_notification(message: Message) -> None:
    """Delete the service message that Telegram sends when someone joins."""
    try:
        await message.delete()
        new_members = ", ".join(
            m.full_name for m in message.new_chat_members
        )
        logger.info(
            "Deleted join notification in chat %s (%s) for: %s",
            message.chat.title,
            message.chat.id,
            new_members,
        )
    except Exception:
        logger.exception(
            "Failed to delete join notification in chat %s (%s)",
            message.chat.title,
            message.chat.id,
        )
