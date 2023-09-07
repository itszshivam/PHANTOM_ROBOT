from typing import Callable

from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message

from FallenRobot import DEV_USERS, pbot


def can_restrict(func: Callable) -> Callable:
    async def non_admin(_, message: Message):
        if message.from_user.id in DEV_USERS:
            return await func(_, message)

        check = await pbot.get_chat_member(message.chat.id, message.from_user.id)
        if check.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return await message.reply_text(
                "=> ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ᴍᴜɴɴᴀ, sᴛᴀʏ ɪɴ ʏᴏᴜʀ ʟɪᴍɪᴛs.. ᴜɴᴅᴇʀsᴛᴏᴏᴅ?."
            )

        admin = (
            await pbot.get_chat_member(message.chat.id, message.from_user.id)
        ).privileges
        if admin.can_restrict_members:
            return await func(_, message)
        else:
            return await message.reply_text(
                "𝐔𝐅𝐅𝐅 !! ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴs ᴛᴏ ʀᴇsᴛʀɪᴄᴛ ᴜsᴇʀs ɪɴ ᴛʜɪs ᴄʜᴀᴛ🥲 𝐒𝐎𝐑𝐑𝐘."
            )

    return non_admin
