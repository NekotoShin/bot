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

from scyllapy.extra_types import BigInt

from ....protocols import CanExecute
from ...utils import to_bigint, to_snowflake

__all__ = ("Counting", "CountingSettingsModel")


@dataclasses.dataclass
class CountingSettingsModel:
    """
    The settings of a dynamic voice channel.
    """

    id: int  # this is here to match the database schema, not processed with the int64/uint64 conversion
    enabled: bool
    channel: int
    current: int
    previous: int
    max: int

    def __post_init__(self):
        self.channel = -1 if self.channel is None else to_snowflake(self.channel)
        self.previous = -1 if self.previous is None else to_snowflake(self.previous)

    @classmethod
    def default(cls) -> "CountingSettingsModel":
        """
        Create a new DvcSettingsModel instance with default values.

        :return: The created DvcSettingsModel instance.
        :rtype: DvcSettingsModel
        """
        return cls(id=0, enabled=False, channel=to_bigint(-1, True), current=0, previous=to_bigint(-1, True), max=0)


class Counting(CanExecute):
    """
    The database class of the bot.
    """

    setup_queries = [
        """
        CREATE TABLE IF NOT EXISTS guild_counting (
            id BIGINT,
            enabled BOOLEAN,
            channel BIGINT,
            current BIGINT,
            previous BIGINT,
            max BIGINT,
            PRIMARY KEY (id)
        );
        """,
    ]

    async def inc_current_count(self, guild_id: int, user_id: int) -> None:
        """
        Increment the current count in the counting game of a guild.

        :param guild_id: The guild ID.
        :type guild_id: int
        :param user_id: The user ID who incremented the count.
        :type user_id: int
        """
        result = await self.execute("SELECT current FROM guild_counting WHERE id = ?;", (to_bigint(guild_id),))
        current = result.first().get("current", 0)
        await self.execute(
            "UPDATE guild_counting SET current = ?, previous = ? WHERE id = ? IF current = ?;",
            (BigInt(current + 1), to_bigint(user_id), to_bigint(guild_id), BigInt(current)),
        )

    async def reset_current_count(self, guild_id: int, current: int) -> None:
        """
        Reset the current count in the counting game of a guild.

        :param guild_id: The guild ID.
        :type guild_id: int
        :param current: The current count.
        :type current: int
        """
        result = await self.execute("SELECT max FROM guild_counting WHERE id = ?;", (to_bigint(guild_id),))
        new_max = max(result.first().get("max", 0), current)
        await self.execute(
            "UPDATE guild_counting SET current = 0, previous = ?, max = ? WHERE id = ?;",
            (BigInt(-1), BigInt(new_max), to_bigint(guild_id)),
        )

    async def get_guild_counting(self, guild_id: int) -> CountingSettingsModel:
        """
        Get the settings of the counting game in a guild.

        :param guild_id: The guild ID.
        :type guild_id: int

        :return: The settings of the counting game.
        :rtype: CountingSettingsModel
        """
        result = await self.execute("SELECT * FROM guild_counting WHERE id = ?;", (to_bigint(guild_id),))
        return result.first(as_class=CountingSettingsModel) or CountingSettingsModel.default()

    async def set_guild_counting(self, guild_id: int, settings: CountingSettingsModel) -> None:
        """
        Set the settings of the counting game in a guild.

        :param guild_id: The guild ID.
        :type guild_id: int
        :param settings: The settings of the counting game.
        :type settings: CountingSettingsModel
        """
        await self.execute(
            "UPDATE guild_counting SET enabled = ?, channel = ?, current = ?, previous = ?, max = ? WHERE id = ?;",
            (
                settings.enabled,
                to_bigint(settings.channel),
                BigInt(settings.current),
                to_bigint(settings.previous),
                BigInt(settings.max),
                to_bigint(guild_id),
            ),
        )
