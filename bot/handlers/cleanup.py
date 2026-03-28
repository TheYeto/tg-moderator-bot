"""On-demand /cleanup command -- batch-deletes any join/leave service
messages that the real-time handler failed to remove."""

import asyncio
import logging

from aiogram import Router
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command
from aiogram.types import Message

from bot.handlers.join_cleanup import pending_service_msg_ids

logger = logging.getLogger(__name__)

router = Router(name="cleanup")


@router.message(Command("cleanup"))
async def cleanup_pending(message: Message) -> None:
    """Retry deletion of any service messages the bot failed to remove.

    Only group admins can trigger this.
    """
    chat = message.chat
    bot = message.bot

    # --- permission check ----------------------------------------------------
    caller = await bot.get_chat_member(chat.id, message.from_user.id)
    if caller.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR):
        await message.reply("Only group admins can run /cleanup.")
        return

    # --- delete the /cleanup command itself -----------------------------------
    try:
        await message.delete()
    except Exception:
        pass

    # --- batch-delete tracked service messages --------------------------------
    ids = pending_service_msg_ids.pop(chat.id, set())

    if not ids:
        notice = await bot.send_message(
            chat.id,
            "Nothing to clean up -- no pending join/leave messages tracked.",
        )
        # auto-delete the notice after a few seconds
        await asyncio.sleep(5)
        try:
            await notice.delete()
        except Exception:
            pass
        return

    deleted = 0
    # Telegram allows deleting up to 100 messages at once
    id_list = sorted(ids)
    for i in range(0, len(id_list), 100):
        batch = id_list[i : i + 100]
        try:
            await bot.delete_messages(chat.id, batch)
            deleted += len(batch)
        except Exception:
            # Fall back to one-by-one
            for mid in batch:
                try:
                    await bot.delete_message(chat.id, mid)
                    deleted += 1
                except Exception:
                    pass

    logger.info(
        "Cleanup in %s (%s): deleted %d / %d queued service messages",
        chat.title,
        chat.id,
        deleted,
        len(ids),
    )
