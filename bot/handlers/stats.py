"""/stats command -- shows how many join/leave messages were deleted today."""

import asyncio
import logging

from aiogram import Router
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command
from aiogram.types import Message

from bot.stats import get_today_count

logger = logging.getLogger(__name__)

router = Router(name="stats")


@router.message(Command("stats"))
async def show_stats(message: Message) -> None:
    """Reply with today's deletion count, then auto-delete both messages."""
    chat = message.chat
    bot = message.bot

    # --- permission check: admins only ---------------------------------------
    caller = await bot.get_chat_member(chat.id, message.from_user.id)
    if caller.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR):
        await message.reply("Only group admins can run /stats.")
        return

    count = get_today_count(chat.id)

    reply = await message.reply(
        f"Deleted {count} join/leave notification{'s' if count != 1 else ''} today (UTC)."
    )

    # Auto-delete both the command and the reply after 10 seconds
    await asyncio.sleep(10)
    for msg in (message, reply):
        try:
            await msg.delete()
        except Exception:
            pass

