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

from ....protocols import CanExecute
from ...models import DvcSettings
from ...utils import to_bigint

__all__ = ("GuildSettings",)


class GuildSettings(CanExecute):
    """
    The database class of the bot.
    """

    async def get_guild_dvc_settings(self, guild_id: int) -> DvcSettings:
        """
        Get the settings of the dynamic voice channels in a guild.

        :param guild_id: The guild ID.
        :type guild_id: int

        :return: The settings of the dynamic voice channels in the guild.
        :rtype: DvcSettings
        """
        result = await self.execute("SELECT dvc FROM guilds WHERE id = ?;", (to_bigint(guild_id),))
        row = result.first()
        return DvcSettings(**row["dvc"]) if row else DvcSettings.default()

    async def set_guild_dvc_settings(self, guild_id: int, settings: DvcSettings) -> None:
        """
        Set the settings of the dynamic voice channels in a guild.

        :param guild_id: The guild ID.
        :type guild_id: int
        :param settings: The settings of the dynamic voice channels.
        :type settings: DvcSettings
        """
        await self.execute("UPDATE guilds SET dvc = ? WHERE id = ?;", (settings, to_bigint(guild_id)))

    async def get_guild_safety_settings(self, guild_id: int) -> dict[str, bool]:
        """
        Get the safety settings of a guild.

        :param guild_id: The guild ID.
        :type guild_id: int

        :return: The safety settings of the guild.
        :rtype: dict[str, bool]
        """
        return {"token": True, "url": True}
