import html
import random

from telegram import MessageEntity, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, Filters, MessageHandler

from FallenRobot import dispatcher
from FallenRobot.modules.disable import (
    DisableAbleCommandHandler,
    DisableAbleMessageHandler,
)
from FallenRobot.modules.sql import afk_sql as sql
from FallenRobot.modules.users import get_user_id

AFK_GROUP = 7
AFK_REPLY_GROUP = 8


def afk(update: Update, context: CallbackContext):
    args = update.effective_message.text.split(None, 1)
    user = update.effective_user

    if not user:  # ignore channels
        return

    if user.id in [777000, 1087968824]:
        return

    notice = ""
    if len(args) >= 2:
        reason = args[1]
        if len(reason) > 100:
            reason = reason[:100]
            notice = "\n𝐘ᴏᴜʀ 𝐀𝐅𝐊 𝐑ᴇᴀsᴏɴ 𝐖ᴀs 𝐒ʜᴏʀᴛᴇɴᴇᴅ 𝐓ᴏ 100 𝐂ʜᴀʀᴀᴄᴛᴇʀs.."
    else:
        reason = ""

    sql.set_afk(update.effective_user.id, reason)
    fname = update.effective_user.first_name
    try:
        update.effective_message.reply_text("{} 𝐈s 𝐍ᴏᴡ 𝐀ᴡᴀʏ!! 𝐃ᴏɴ'ᴛ 𝐃ɪsᴛᴜʀʙ.🤫{}".format(fname, notice))
    except BadRequest:
        pass


def no_longer_afk(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.effective_message

    if not user:  # ignore channels
        return

    res = sql.rm_afk(user.id)
    if res:
        if message.new_chat_members:  # dont say msg
            return
        firstname = update.effective_user.first_name
        try:
            options = [
                "{} 𝐈s 𝐇ᴇʀᴇ!!🤩",
                "{} 𝐈s 𝐁ᴀᴄᴋ!!😍",
                "{} 𝐈s 𝐍ᴏᴡ 𝐈ɴ 𝐓ʜᴇ 𝐂ʜᴀᴛ!!😜",
                "{} 𝐇ᴀs 𝐀ᴡᴀᴋᴇɴ!!🥰",
                "{} 𝐈s 𝐁ᴀᴄᴋ 𝐎ɴ 𝐓ᴇʟᴇɢʀᴀᴍ!!😋",
                "{} 𝐈s 𝐅ɪɴᴀʟʟʏ 𝐇ᴇʀᴇ!!😍",
                "𝐖ᴇʟᴄᴏᴍᴇ 𝐀ɢᴀɪɴ!! {} 🤗",
                "𝐖ʜᴇʀᴇ 𝐈s? {}?\n𝐈ɴ 𝐓ʜᴇ 𝐂ʜᴀᴛ!!😎",
            ]
            chosen_option = random.choice(options)
            update.effective_message.reply_text(chosen_option.format(firstname))
        except:
            return


def reply_afk(update: Update, context: CallbackContext):
    bot = context.bot
    message = update.effective_message
    userc = update.effective_user
    userc_id = userc.id
    if message.entities and message.parse_entities(
        [MessageEntity.TEXT_MENTION, MessageEntity.MENTION]
    ):
        entities = message.parse_entities(
            [MessageEntity.TEXT_MENTION, MessageEntity.MENTION]
        )

        chk_users = []
        for ent in entities:
            if ent.type == MessageEntity.TEXT_MENTION:
                user_id = ent.user.id
                fst_name = ent.user.first_name

                if user_id in chk_users:
                    return
                chk_users.append(user_id)

            if ent.type != MessageEntity.MENTION:
                return

            user_id = get_user_id(message.text[ent.offset : ent.offset + ent.length])
            if not user_id:
                # Should never happen, since for a user to become AFK they must have spoken. Maybe changed username?
                return

            if user_id in chk_users:
                return
            chk_users.append(user_id)

            try:
                chat = bot.get_chat(user_id)
            except BadRequest:
                print("ᴇʀʀᴏʀ✖️ 𝐂ᴏᴜʟᴅ 𝐍ᴏᴛ 𝐅ᴇᴛᴄʜ 𝐔sᴇʀ 𝐈'ᴅ {} 𝐅ᴏʀ 𝐀𝐅𝐊 𝐌ᴏᴅᴜʟᴇ".format(user_id))
                return
            fst_name = chat.first_name

            check_afk(update, context, user_id, fst_name, userc_id)

    elif message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        fst_name = message.reply_to_message.from_user.first_name
        check_afk(update, context, user_id, fst_name, userc_id)


def check_afk(update, context, user_id, fst_name, userc_id):
    if sql.is_afk(user_id):
        user = sql.check_afk_status(user_id)
        if int(userc_id) == int(user_id):
            return
        if not user.reason:
            res = "{} is afk".format(fst_name)
            update.effective_message.reply_text(res)
        else:
            res = "{} is afk.\nReason: <code>{}</code>".format(
                html.escape(fst_name), html.escape(user.reason)
            )
            update.effective_message.reply_text(res, parse_mode="html")


__help__ = """
*⁠☞ 𝐀ᴡᴀʏ 𝐅ʀᴏᴍ 𝐊ᴇʏʙᴏᴀʀᴅ (𝐀𝐅𝐊)*
 ➥ /afk <reason>*➝* 𝐌ᴀʀᴋ 𝐘ᴏᴜʀsᴇʟғ 𝐀s 𝐀𝐅𝐊.
 ➥ brb <reason>*➝* 𝐒ᴀᴍᴇ 𝐀s 𝐀𝐅𝐊 𝐁ᴜᴛ 𝐘ᴏᴜ 𝐃ɪᴅɴ'ᴛ 𝐇ᴀᴠᴇ 𝐓ᴏ 𝐖ʀɪᴛᴇ / ..
"""

AFK_HANDLER = DisableAbleCommandHandler("afk", afk, run_async=True)
AFK_REGEX_HANDLER = DisableAbleMessageHandler(
    Filters.regex(r"^(?i)brb(.*)$"), afk, friendly="afk", run_async=True
)
NO_AFK_HANDLER = MessageHandler(
    Filters.all & Filters.chat_type.groups, no_longer_afk, run_async=True
)
AFK_REPLY_HANDLER = MessageHandler(
    Filters.all & Filters.chat_type.groups, reply_afk, run_async=True
)

dispatcher.add_handler(AFK_HANDLER, AFK_GROUP)
dispatcher.add_handler(AFK_REGEX_HANDLER, AFK_GROUP)
dispatcher.add_handler(NO_AFK_HANDLER, AFK_GROUP)
dispatcher.add_handler(AFK_REPLY_HANDLER, AFK_REPLY_GROUP)

__mod_name__ = "𝐀𝐅𝐊💥​"
__command_list__ = ["afk"]
__handlers__ = [
    (AFK_HANDLER, AFK_GROUP),
    (AFK_REGEX_HANDLER, AFK_GROUP),
    (NO_AFK_HANDLER, AFK_GROUP),
    (AFK_REPLY_HANDLER, AFK_REPLY_GROUP),
]
