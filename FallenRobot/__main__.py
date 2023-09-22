import importlib
import re
import time
from platform import python_version as y
from sys import argv

from pyrogram import __version__ as pyrover
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram import __version__ as telever
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop
from telegram.utils.helpers import escape_markdown
from telethon import __version__ as tlhver

import FallenRobot.modules.sql.users_sql as sql
from FallenRobot import (
    BOT_NAME,
    BOT_USERNAME,
    LOGGER,
    OWNER_ID,
    START_IMG,
    SUPPORT_CHAT,
    TOKEN,
    StartTime,
    dispatcher,
    pbot,
    telethn,
    updater,
)
from FallenRobot.modules import ALL_MODULES
from FallenRobot.modules.helper_funcs.chat_status import is_user_admin
from FallenRobot.modules.helper_funcs.misc import paginate_modules


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


PM_START_TEXT = """
*𝐇𝐄𝐘* {}, 🥀

*🍷𝐖ᴇʟᴄᴏᴍᴇ 𝐓ᴏ* {} 🍷

🌹𝐈 𝐀𝐦 𝐓𝐡𝐞 𝐌𝐨𝐬𝐭 𝐏𝐨𝐰𝐞𝐫𝐟𝐮𝐥 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦 𝐆𝐫𝐨𝐮𝐩 𝐌𝐚𝐧𝐚𝐠𝐞𝐦𝐞𝐧𝐭 𝐁𝐨𝐭 𝐖𝐢𝐭𝐡 𝐌𝐚𝐧𝐲 𝐅𝐚𝐧𝐭𝐚𝐬𝐭𝐢𝐜 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬..🌹
─────────────────
🥳𝐀𝐝𝐝 𝐌𝐞 𝐈𝐧 𝐘𝐨𝐮𝐫 𝐆𝐫𝐨𝐮𝐩𝐬 𝐓𝐨 𝐌𝐚𝐧𝐚𝐠𝐞 𝐈𝐭 𝐕𝐞𝐫𝐲 𝐒𝐦𝐨𝐨𝐭𝐡𝐥𝐲 𝐚𝐧𝐝 𝐄𝐧𝐣𝐨𝐲 𝐀𝐥𝐥 𝐌𝐲 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬..🥳
─────────────────
💞𝐂𝐥𝐢𝐜𝐤 𝐎𝐧 𝐓𝐡𝐞 𝐇𝐞𝐥𝐩 𝐁𝐮𝐭𝐭𝐨𝐧 𝐓𝐨 𝐆𝐞𝐭 𝐈𝐧𝐟𝐨𝐫𝐦𝐚𝐭𝐢𝐨𝐧 𝐀𝐛𝐨𝐮𝐭 𝐀𝐥𝐥 𝐓𝐡𝐞 𝐌𝐨𝐝𝐮𝐥𝐞𝐬 𝐀𝐧𝐝 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬.. 💞
"""

buttons = [
    [
        InlineKeyboardButton(
            text="•🌷𝐀∂𝐃 𝐌𝐞 𝐓𝐨 𝐘συ𝐑 𝐆яσυ𝐏🌷•",
            url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
        ),
    ],
    [
        InlineKeyboardButton(text="𝐇єℓ𝐏 ☆ 𝐂σммαи∂𝐒", callback_data="help_back"),
    ],
    [
        InlineKeyboardButton(text="🌸𝐀вσυ𝐓🌸", callback_data="fallen_"),
        InlineKeyboardButton(text="⚡𝐒υρρσя𝐓⚡", url=f"https://t.me/{SUPPORT_CHAT}"),
    ],
    [
        InlineKeyboardButton(text="🌹𝐃єνєℓσρє𝐑🌹", url=f"tg://user?id={OWNER_ID}"),
        InlineKeyboardButton(text="🎧𝐌υѕι𝐂🎧", url=f"https://t.me/phantom_musicbot"),
    ],
]

HELP_STRINGS = f"""
*🌟 <u>𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐇𝐄𝐋𝐏 𝐒𝐄𝐂𝐓𝐈𝐎𝐍</u> *

✨ 𝐂ʟɪᴄᴋ 𝐎ɴ 𝐓ʜᴇ 𝐁ᴇʟᴏᴡ 𝐁ᴜᴛᴛᴏɴs 𝐅ᴏʀ 𝐌ᴏʀᴇ 𝐈ɴғᴏʀᴍᴀᴛɪᴏɴ ✨ ...

🥀𝐈ғ 𝐘ᴏᴜ 𝐀ʀᴇ 𝐅ᴀᴄɪɴɢ » 𝐀ɴʏ 𝐏ʀᴏʙʟᴇᴍs ɪɴ 𝐂ᴏᴍᴍᴀɴᴅs 𝐓ʜᴇɴ ❥︎ 𝐘ᴏᴜ 𝐂ᴀɴ 𝐂ᴏɴᴛᴀᴄᴛ 𝐓ᴏ 𝐌ʏ [𝐎ᴡɴᴇʀ](https://t.me/itsz_shivam) ❥︎ 𝐎ʀ 𝐀sᴋ ɪɴ ❥︎ 𝐎ᴜʀ [𝐒ᴜᴘᴘᴏʀᴛ 𝐂ʜᴀᴛ](https://t.me/fun_here) 💞 ...

➥ 𝐓ʏᴘᴇ /help 𝐅ᴏʀ 𝐆ᴇᴛᴛɪɴɢ 𝐂ᴏᴍᴍᴀɴᴅs 𝐒ᴇᴄᴛɪᴏɴ..😇

🌷𝐀ʟʟ 𝐂ᴏᴍᴍᴀɴᴅs 𝐂ᴀɴ 𝐁ᴇ 𝐔sᴇᴅ 𝐖ɪᴛʜ /🌷"""

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("FallenRobot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


def start(update: Update, context: CallbackContext):
    args = context.args
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="⏎", callback_data="help_back")]]
                    ),
                )

            elif args[0].lower() == "markdownhelp":
                IMPORTED["exᴛʀᴀs"].markdown_help_sender(update)
            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rᴜʟᴇs" in IMPORTED:
                IMPORTED["rᴜʟᴇs"].send_rules(update, args[0], from_pm=True)

        else:
            first_name = update.effective_user.first_name
            update.effective_message.reply_sticker(
                "CAACAgQAAx0Cb8p2IgACM8tlDKevrMnTjx1EJWgTsMUWRMzIwQAC8xEAAjGRAVJKnNWa5ijzlh4E"
            )
            update.effective_message.reply_text(
                PM_START_TEXT.format(escape_markdown(first_name), BOT_NAME),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
            )
    else:
        update.effective_message.reply_photo(
            START_IMG,
            caption="𝐈 𝐀ᴍ 𝐀ʟɪᴠᴇ 𝐃ᴜᴅᴇ !!\n<b>𝐈 𝐃ɪᴅɴ'ᴛ 𝐒ʟᴇᴘᴛ 𝐒ɪɴᴄᴇ​:</b> <code>{}</code>".format(
                uptime
            ),
            parse_mode=ParseMode.HTML,
        )


def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML)


# for test purposes
def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors


def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "🌟 *𝐀ναιʅαвʅ𝐄 𝐂σммαи∂𝐒 𝐅ᴏ𝐑* *{}* :\n".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].__help__
            )
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="⏎", callback_data="help_back")]]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        context.bot.answer_callback_query(query.id)

    except BadRequest:
        pass


def Fallen_about_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "fallen_":
        uptime = get_readable_time((time.time() - StartTime))
        query.message.edit_text(
            text=f"*𝐇𝐄𝐋𝐋𝐎,,*🌹\n\n  *𝐓ʜɪs 𝐈s {BOT_NAME}*"
            "\n\n*𝐓ʜᴇ 𝐌ᴏsᴛ 𝐏ᴏᴡᴇʀꜰᴜʟ 𝐁ᴏᴛ 𝐅ᴏʀ 𝐌ᴀɴᴀɢɪɴɢ 𝐘ᴏᴜʀ 𝐆ʀᴏᴜᴘ𝐬.🥰*"
            "\n\n────────────────────"
            f"\n*➻ 𝐔𝙿𝚃𝙸𝙼𝙴 »* {uptime}"
            f"\n*➻ 𝐔𝚂𝙴𝚁𝚂 »* {sql.num_users()}"
            f"\n*➻ 𝐂𝙷𝙰𝚃𝚂 »* {sql.num_chats()}"
            "\n────────────────────"
            "\n\n➥  𝐈 𝐂ᴀɴ 𝐑ᴇꜱᴛʀɪᴄᴛ 𝐔ꜱᴇʀꜱ..🤩"
            "\n➥  𝐈 𝐇ᴀᴠᴇ 𝐀ɴ 𝐀ᴅᴠᴀɴᴄᴇᴅ 𝐀ɴᴛɪ~𝐅ʟᴏᴏᴅ 𝐒ʏꜱᴛᴇᴍ..🤩"
            "\n➥  𝐈 𝐂ᴀɴ 𝐆ʀᴇᴇᴛ 𝐔ꜱᴇʀꜱ 𝐖ɪᴛʜ 𝐂ᴜꜱᴛᴏᴍɪᴢᴀʙʟᴇ 𝐖ᴇʟᴄᴏᴍᴇ 𝐌ᴇssᴀɢᴇs 𝐀ɴᴅ 𝐄ᴠᴇɴ 𝐒ᴇᴛ 𝐀 𝐆ʀᴏᴜᴘ'ꜱ 𝐑ᴜʟᴇꜱ..🤩"
            "\n➥  𝐈 𝐂ᴀɴ 𝐖ᴀʀɴ, 𝐌ᴜᴛᴇ, 𝐁ᴀɴ 𝐀ɴᴅ 𝐊ɪᴄᴋ 𝐔ꜱᴇʀꜱ..🤩"
            "\n➥  𝐈 𝐇ᴀᴠᴇ 𝐀 𝐍ᴏᴛᴇ 𝐊ᴇᴇᴘɪɴɢ 𝐒ʏꜱᴛᴇᴍ, 𝐁ʟᴀᴄᴋʟɪꜱᴛꜱ, 𝐀ɴᴅ 𝐅ɪʟᴛᴇʀs » 𝐖ᴏʀᴋs 𝐎ɴʟʏ 𝐈ɴ 𝐆ʀᴏᴜᴘs..🤩"
            f"\n\n➼ 𝐂ʟɪᴄᴋ 𝐎ɴ 𝐓ʜᴇ 𝐁ᴜᴛᴛᴏɴs 𝐆ɪᴠᴇɴ 𝐁ᴇʟᴏᴡ 𝐅ᴏʀ 𝐆ᴇᴛᴛɪɴɢ 𝐁ᴀsɪᴄ 𝐇ᴇʟᴩ 𝐀ɴᴅ 𝐈ɴғᴏ...🌷",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="⚡𝐒υρρσя𝐓⚡", url=f"https://t.me/fun_here"
                        ),
                        InlineKeyboardButton(
                            text="🌹𝐇єʅ𝐏🌹", callback_data="help_back"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="✨𝐃єνєℓσρє𝐑✨", url=f"tg://user?id={OWNER_ID}"
                        ),
                        InlineKeyboardButton(
                            text="⭐𝐔ρ∂αтє𝐒⭐", url=f"https://t.me/over_poweredd"
                        ),
                    ],
                    [
                        InlineKeyboardButton(text="⏎", callback_data="fallen_back"),
                    ],
                ]
            ),
        )
    elif query.data == "fallen_support":
        query.message.edit_text(
            text="*๏ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ʜᴇʟᴩ ᴀɴᴅ ᴍᴏʀᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍᴇ.*"
            f"\n\nɪғ ʏᴏᴜ ғᴏᴜɴᴅ ᴀɴʏ ʙᴜɢ ɪɴ {BOT_NAME} ᴏʀ ɪғ ʏᴏᴜ ᴡᴀɴɴᴀ ɢɪᴠᴇ ғᴇᴇᴅʙᴀᴄᴋ ᴀʙᴏᴜᴛ ᴛʜᴇ {BOT_NAME}, ᴩʟᴇᴀsᴇ ʀᴇᴩᴏʀᴛ ɪᴛ ᴀᴛ sᴜᴩᴩᴏʀᴛ ᴄʜᴀᴛ.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="sᴜᴩᴩᴏʀᴛ", url=f"https://t.me/{SUPPORT_CHAT}"
                        ),
                        InlineKeyboardButton(
                            text="ᴜᴩᴅᴀᴛᴇs", url=f"https://t.me/{SUPPORT_CHAT}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="ᴅᴇᴠᴇʟᴏᴩᴇʀ", url=f"tg://user?id={OWNER_ID}"
                        ),
                        InlineKeyboardButton(
                            text="ɢɪᴛʜᴜʙ",
                            url="https://github.com/itszshivam",
                        ),
                    ],
                    [
                        InlineKeyboardButton(text="⏎", callback_data="fallen_"),
                    ],
                ]
            ),
        )
    elif query.data == "fallen_back":
        first_name = update.effective_user.first_name
        query.message.edit_text(
            PM_START_TEXT.format(escape_markdown(first_name), BOT_NAME),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,
            disable_web_page_preview=True,
        )


def Source_about_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "source_":
        query.message.edit_text(
            text=f"""
*ʜᴇʏ,
 ᴛʜɪs ɪs {BOT_NAME},
ᴀɴ ᴏᴩᴇɴ sᴏᴜʀᴄᴇ ᴛᴇʟᴇɢʀᴀᴍ ɢʀᴏᴜᴩ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ.*

ᴡʀɪᴛᴛᴇɴ ɪɴ ᴩʏᴛʜᴏɴ ᴡɪᴛʜ ᴛʜᴇ ʜᴇʟᴩ ᴏғ : [ᴛᴇʟᴇᴛʜᴏɴ](https://github.com/LonamiWebs/Telethon)
[ᴩʏʀᴏɢʀᴀᴍ](https://github.com/pyrogram/pyrogram)
[ᴩʏᴛʜᴏɴ-ᴛᴇʟᴇɢʀᴀᴍ-ʙᴏᴛ](https://github.com/python-telegram-bot/python-telegram-bot)
ᴀɴᴅ ᴜsɪɴɢ [sǫʟᴀʟᴄʜᴇᴍʏ](https://www.sqlalchemy.org) ᴀɴᴅ [ᴍᴏɴɢᴏ](https://cloud.mongodb.com) ᴀs ᴅᴀᴛᴀʙᴀsᴇ.


*ʜᴇʀᴇ ɪs ᴍʏ sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ :* [ɢɪᴛʜᴜʙ](https://github.com/AnonymousX1025/FallenRobot)


{BOT_NAME} ɪs ʟɪᴄᴇɴsᴇᴅ ᴜɴᴅᴇʀ ᴛʜᴇ [ᴍɪᴛ ʟɪᴄᴇɴsᴇ](https://github.com/AnonymousX1025/FallenRobot/blob/master/LICENSE).
© 2022 - 2023 | [sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ](https://t.me/{SUPPORT_CHAT}), ᴀʟʟ ʀɪɢʜᴛs ʀᴇsᴇʀᴠᴇᴅ.
""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="⏎", callback_data="source_back")]]
            ),
        )
    elif query.data == "source_back":
        first_name = update.effective_user.first_name
        query.message.edit_text(
            PM_START_TEXT.format(escape_markdown(first_name), BOT_NAME),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,
            disable_web_page_preview=True,
        )


def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_text(
                f"𝐂ᴏɴᴛᴀᴄᴛ 𝐌ᴇ 𝐈ɴ 𝐊ʜᴏᴘᴄʜᴀ(𝐏𝐌) 𝐅ᴏʀ 𝐓ʜɪs {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="𝐇ꫀʅ𝐏",
                                url="https://t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_text(
            "🌟 𝐂ʜᴏᴏsᴇ 𝐀ɴ 𝐎ᴘᴛɪᴏɴ 𝐅ᴏʀ 𝐆ᴇᴛᴛɪɴɢ 𝐇ᴇʟᴘ.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="𝐎ᴘᴇɴ 𝐈ɴ 𝐊ʜᴏᴘᴄʜᴀ(𝐏𝐌)",
                            url="https://t.me/{}?start=help".format(
                                context.bot.username
                            ),
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="𝐎ᴩᴇɴ 𝐇ᴇʀᴇ",
                            callback_data="help_back",
                        )
                    ],
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "🌟 𝐇ᴇʀᴇ 𝐈s 𝐓ʜᴇ 𝐀ᴠᴀɪʟᴀʙʟᴇ 𝐇ᴇʟᴘ 𝐅ᴏʀ 𝐓ʜᴇ *{}* module:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="⏎", callback_data="help_back")]]
            ),
        )

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?".format(
                    chat_name
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )


def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="⏎",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))


def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Click here to get this chat's settings, as well as yours."
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="𝐒ᴇᴛᴛɪɴɢ𝐒",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "Click here to check your settings."

    else:
        send_settings(chat.id, user.id, True)


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise DispatcherHandlerStop


def main():
    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.send_photo(
                chat_id=f"@{SUPPORT_CHAT}",
                photo=START_IMG,
                caption=f"""
ㅤㅤ🌹 {BOT_NAME} 𝐈s 𝐀ʟɪᴠᴇ 𝐃ᴜᴅᴇ..☆

┏•☆────✧☆✦☆✧────☆•┓
ㅤ★ 𝐏утнσ𝐍 ➪ {y()}
ㅤ★ 𝐋ιвяαя𝐘 ➪ {telever}
ㅤ★ 𝐓єℓєтнσ𝐍 ➪ {tlhver}
ㅤ★ 𝐏уяσgяαм𝐌 ➪ {pyrover}
┗•☆────✧☆✦☆✧────☆•┛""",
                parse_mode=ParseMode.MARKDOWN,
            )
        except Unauthorized:
            LOGGER.warning(
                f"Bot isn't able to send message to @{SUPPORT_CHAT}, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)

    start_handler = CommandHandler("start", start, run_async=True)

    help_handler = CommandHandler("help", get_help, run_async=True)
    help_callback_handler = CallbackQueryHandler(
        help_button, pattern=r"help_.*", run_async=True
    )

    settings_handler = CommandHandler("settings", get_settings, run_async=True)
    settings_callback_handler = CallbackQueryHandler(
        settings_button, pattern=r"stngs_", run_async=True
    )

    about_callback_handler = CallbackQueryHandler(
        Fallen_about_callback, pattern=r"fallen_", run_async=True
    )
    source_callback_handler = CallbackQueryHandler(
        Source_about_callback, pattern=r"source_", run_async=True
    )

    migrate_handler = MessageHandler(Filters.status_update.migrate, migrate_chats)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(about_callback_handler)
    dispatcher.add_handler(source_callback_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)

    dispatcher.add_error_handler(error_callback)

    LOGGER.info("Using long polling.")
    updater.start_polling(timeout=15, read_latency=4, drop_pending_updates=True)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()

    updater.idle()


if __name__ == "__main__":
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    pbot.start()
    main()
