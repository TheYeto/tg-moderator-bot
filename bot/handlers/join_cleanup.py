"""Handler that deletes 'new member joined' service messages.

Also tracks join message IDs so /cleanup can batch-delete any that
slipped through (e.g. during a brief outage or race condition).
"""

import logging
from collections import defaultdict

from aiogram import F, Router
from aiogram.types import Message

from bot.stats import record_deletion

logger = logging.getLogger(__name__)

router = Router(name="join_cleanup")

# chat_id -> set of message IDs that are join/leave service messages.
# Kept in memory; lost on restart, but that's fine — the real-time
# handler deletes them immediately, and /cleanup is a safety net.
pending_service_msg_ids: dict[int, set[int]] = defaultdict(set)


@router.message(F.new_chat_members)
async def delete_join_notification(message: Message) -> None:
    """Delete the service message that Telegram sends when someone joins."""
    try:
        await message.delete()
        record_deletion(message.chat.id)
        new_members = ", ".join(
            m.full_name for m in message.new_chat_members  # type: ignore[union-attr]
        )
        logger.info(
            "Deleted join notification in chat %s (%s) for: %s",
            message.chat.title,
            message.chat.id,
            new_members,
        )
    except Exception:
        # Deletion failed — track the ID so /cleanup can retry later
        pending_service_msg_ids[message.chat.id].add(message.message_id)
        logger.exception(
            "Failed to delete join notification in chat %s (%s), queued for /cleanup",
            message.chat.title,
            message.chat.id,
        )


@router.message(F.left_chat_member)
async def delete_left_notification(message: Message) -> None:
    """Delete the service message that Telegram sends when someone leaves."""
    try:
        await message.delete()
        record_deletion(message.chat.id)
        logger.info(
            "Deleted leave notification in chat %s (%s) for: %s",
            message.chat.title,
            message.chat.id,
            message.left_chat_member.full_name,  # type: ignore[union-attr]
        )
    except Exception:
        pending_service_msg_ids[message.chat.id].add(message.message_id)
        logger.exception(
            "Failed to delete leave notification in chat %s (%s), queued for /cleanup",
            message.chat.title,
            message.chat.id,
        )
