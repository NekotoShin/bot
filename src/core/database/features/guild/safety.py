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

import dataclasses

from ....protocols import CanExecute
from ...utils import to_bigint

__all__ = ("Safety", "SafetySettingsModel")


@dataclasses.dataclass
class SafetySettingsModel:
    """
    The safety settings of a guild.
    """

    id: int  # this is here to match the database schema, not processed with the int64/uint64 conversion
    dtoken: bool
    url: bool

    @property
    def enabled(self) -> bool:
        """
        Check if any safety setting is enabled.

        :return: Whether any safety setting is enabled.
        :rtype: bool
        """
        return self.dtoken or self.url

    @classmethod
    def default(cls) -> "SafetySettingsModel":
        """
        Create a new SafetySettingsModel instance with default values.

        :return: The created SafetySettingsModel instance.
        :rtype: SafetySettingsModel
        """
        return cls(0, dtoken=True, url=True)


class Safety(CanExecute):
    """
    The database class of the bot.
    """

    setup_queries = [
        """
        CREATE TABLE IF NOT EXISTS guild_safety (
            id BIGINT,
            dtoken BOOLEAN,
            url BOOLEAN,
            PRIMARY KEY (id)
        );
        """
    ]

    async def get_guild_safety_settings(self, guild_id: int) -> SafetySettingsModel:
        """
        Get the safety settings of a guild.

        :param guild_id: The guild ID.
        :type guild_id: int

        :return: The safety settings of the guild.
        :rtype: SafetySettingsModel
        """
        result = await self.execute("SELECT * FROM guild_safety WHERE id = ?;", (to_bigint(guild_id),))
        return result.first(as_class=SafetySettingsModel) or SafetySettingsModel.default()

    async def set_guild_safety_settings(self, guild_id: int, settings: SafetySettingsModel) -> None:
        """
        Set the safety settings of a guild.

        :param guild_id: The guild ID.
        :type guild_id: int
        :param settings: The safety settings.
        :type settings: SafetySettingsModel
        """
        await self.execute(
            "UPDATE guild_safety SET dtoken = ?, url = ? WHERE id = ?;",
            (settings.dtoken, settings.url, to_bigint(guild_id)),
        )
