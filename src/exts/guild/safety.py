"""
Copyright (C) 2024  猫戸シン

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import contextlib

import aiohttp
import decouple
import interactions  # noqa: F401

from src.main import BaseExtension, Client
from src.utils import Embed, Validator


class Safety(BaseExtension):
    """
    The extension class for the [purpose].
    """

    async def _handle_tokens(self, event: interactions.events.MessageCreate) -> bool:
        """
        Handle the tokens in a message.

        :param event: The event object.
        :type event: interactions.events.MessageCreate

        :return: If the subsquent checks should be skipped.
        :rtype: bool
        """
        tokens = Validator.find_tokens(event.message.content)
        for i in tokens:
            if await Validator.is_valid_token(i):
                try:
                    await event.message.delete()
                except interactions.errors.HTTPException:
                    with contextlib.suppress(interactions.errors.HTTPException):
                        await event.message.reply(
                            event.message.author.mention,
                            embed=Embed(
                                "你的訊息包含了Discord token、但沒有足夠權限刪除訊息！\n"
                                "為安全起見請前往 [Discord Developer Portal]"
                                "(<https://discord.com/developers/applications>) 進行重設。",
                                success=False,
                            ),
                        )
                else:
                    with contextlib.suppress(interactions.errors.HTTPException):
                        await event.message.channel.send(
                            event.message.author.mention,
                            embed=Embed(
                                "你的訊息包含了Discord token！\n"
                                "為安全起見請前往 [Discord Developer Portal]"
                                "(<https://discord.com/developers/applications>) 進行重設。"
                            ),
                        )
                        return True
                break
        return False

    async def _handle_urls(self, event: interactions.events.MessageCreate) -> bool:
        """
        Handle the URLs in a message.
        URL for testing: http://malware.testing.google.test/testing/malware/

        :param event: The event object.
        :type event: interactions.events.MessageCreate

        :return: If the subsequent checks should be skipped.
        :rtype: bool
        """
        urls = Validator.find_urls(event.message.content)
        async with aiohttp.ClientSession() as s, s.post(
            f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={decouple.config('googleapi')}",
            json={
                "client": {"clientId": "猫戸助手", "clientVersion": self.client.__version__},
                "threatInfo": {
                    "threatTypes": [
                        "MALWARE",
                        "SOCIAL_ENGINEERING",
                        "UNWANTED_SOFTWARE",
                        "POTENTIALLY_HARMFUL_APPLICATION",
                    ],
                    "platformTypes": ["ANY_PLATFORM"],
                    "threatEntryTypes": ["URL"],
                    "threatEntries": [{"url": i} for i in [*{"".join(i) for i in urls}]],
                },
            },
        ) as r:
            resp = await r.json()
        if "matches" in resp:
            embed = Embed("檢測到可能有害的連結了！\n資料僅供參考，未必完全準確，請自行注意連結是否安全喔～")
            embed.set_footer(text="Google Safe Browsing API")
            with contextlib.suppress(interactions.errors.HTTPException):
                await event.message.reply(embed=embed)
        return False

    @interactions.listen("on_message_create")
    async def on_message_create(self, event: interactions.events.MessageCreate):
        """
        The event for when a message is created.

        :param event: The event object.
        :type event: interactions.events.MessageCreate
        """
        if event.message.author.bot or event.message.author.system:
            return
        if not event.message.guild or not event.message.content:
            return

        checks = await self.database.get_guild_safety_settings(event.message.guild.id)

        if checks["token"] and await self._handle_tokens(event):
            return

        if checks["url"] and await self._handle_urls(event):
            return


def setup(client: Client):
    """
    The setup function for the extension.

    :param client: The client object.
    :type client: Client
    """
    Safety(client)
