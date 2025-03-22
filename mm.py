import logging

from telethon.errors.rpcerrorlist import BotMethodInvalidError, FloodWaitError, MessageNotModifiedError
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class MusicMod(loader.Module):
    strings = {
        "name": "Music",
        "no_query": "<emoji document_id=5337117114392127164>🤷‍♂</emoji> <b>Provide a search query.</b>",
        "searching": "<emoji document_id=5258396243666681152>🔎</emoji> <b>Searching...</b>",
        "not_found": "<emoji document_id=5843952899184398024>🚫</emoji> <b>Track not found</b>",
        "invalid_service": "<emoji document_id=5462295343642956603>🚫</emoji> <b>Invalid service. Use yandex/ya, vk, sc</b>",
        "usage": "<b>Usage:</b> <code>.music [yandex|vk|sc] [track name]</code>",
        "error": "<emoji document_id=5843952899184398024>🚫</emoji> <b>Error: {}</b>",
        "flood_wait": "<emoji document_id=5462295343642956603>⏳</emoji> <b>Wait {}s (Telegram limits).</b>",
        "bot_error": "<emoji document_id=5228947933545635555>🤖</emoji> <b>Bot error: {}</b>",
    }

    def __init__(self):
        self.murglar_bot = "@murglar_bot"
        self.service_map = {
            "ya": "ynd",
            "vk": "vk",
            "sc": "sc"
        }

    @loader.command()
    async def music(self, message: Message):
        args = utils.get_args(message)

        if not args:
            if reply := await message.get_reply_message():
                await self._search(message, "ynd", reply.raw_text.strip())
            else:
                await utils.answer(message, self.strings("usage"))
            return

        service = args[0].lower()
        if service not in self.service_map:
            await utils.answer(message, self.strings("invalid_service"))
            return

        await self._search(
            message,
            self.service_map[service],
            " ".join(args[1:]) if len(args) > 1 else ""
        )

    async def _search(self, message: Message, service: str, query: str):
        if not query:
            await utils.answer(message, self.strings("no_query"))
            return

        await utils.answer(message, self.strings("searching"))

        try:
            results = await message.client.inline_query(
                self.murglar_bot,
                f"s:{service} {query}"
            )

            if not results:
                await utils.answer(message, self.strings("not_found"))
                return

            await results[0].click(
                entity=message.chat_id,
                hide_via=True,
                reply_to=message.reply_to_msg_id or None
            )
            await message.delete()

        except FloodWaitError as e:
            await utils.answer(message, self.strings("flood_wait").format(e.seconds))
        except BotMethodInvalidError as e:
            await utils.answer(message, self.strings("bot_error").format(str(e)))
        except MessageNotModifiedError:
            pass
        except Exception as e:
            logger.exception("Search error:")
            await utils.answer(message, self.strings("error").format(str(e)))