"""/stats command -- DM-only. Shows deletion counts for all moderated groups."""

import logging

from aiogram import Router
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.filters import Command
from aiogram.types import Message

from bot.stats import get_all_today_counts

logger = logging.getLogger(__name__)

router = Router(name="stats")


@router.message(Command("stats"))
async def show_stats(message: Message) -> None:
    """Reply with today's deletion counts (DM only, admin only)."""

    # ---- only respond in private DMs ------------------------------------
    if message.chat.type != ChatType.PRIVATE:
        return  # silently ignore in groups

    bot = message.bot
    user_id = message.from_user.id
    counts = get_all_today_counts()

    if not counts:
        await message.answer("No deletions recorded today (UTC).")
        return

    lines: list[str] = []
    for chat_id, count in counts.items():
        # verify caller is admin in this group
        try:
            member = await bot.get_chat_member(chat_id, user_id)
        except Exception:
            continue  # bot can't reach this chat or user isn't in it
        if member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR):
            continue

        # get group title
        try:
            chat = await bot.get_chat(chat_id)
            title = chat.title or str(chat_id)
        except Exception:
            title = str(chat_id)

        s = "s" if count != 1 else ""
        lines.append(f"\u2022 {title}: {count} notification{s} deleted")

    if lines:
        header = "Today's stats (UTC):\n\n"
        await message.answer(header + "\n".join(lines))
    else:
        await message.answer("You're not an admin in any groups I'm moderating.")
