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
from typing import AsyncGenerator

from ....protocols import CanExecute
from ...utils import to_bigint, to_snowflake

__all__ = ("Dvc", "DvcSettingsModel")


@dataclasses.dataclass
class DvcSettingsModel:
    """
    The settings of a dynamic voice channel.
    """

    id: int  # this is here to match the database schema, not processed with the int64/uint64 conversion
    enabled: bool
    lobby: int
    name: str

    def __post_init__(self):
        self.lobby = -1 if self.lobby is None else to_snowflake(self.lobby)

    @classmethod
    def default(cls) -> "DvcSettingsModel":
        """
        Create a new DvcSettingsModel instance with default values.

        :return: The created DvcSettingsModel instance.
        :rtype: DvcSettingsModel
        """
        return cls(id=0, enabled=False, lobby=to_bigint(-1, True), name=None)


class Dvc(CanExecute):
    """
    The database class of the bot.
    """

    setup_queries = [
        """
        CREATE TABLE IF NOT EXISTS feature_dvc (
            id BIGINT,
            owner_id BIGINT,
            guild_id BIGINT,
            PRIMARY KEY (id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS guild_dvc (
            id BIGINT,
            enabled BOOLEAN,
            lobby BIGINT,
            name TEXT,
            PRIMARY KEY (id)
        );
        """,
    ]

    async def is_dvc(self, channel_id: int) -> bool:
        """
        Checks if a channel is a dynamic voice channel.

        :param channel_id: The channel ID.
        :type channel_id: int

        :return: Whether the channel is a dynamic voice channel.
        :rtype: bool
        """
        result = await self.execute("SELECT COUNT(*) FROM feature_dvc WHERE id = ?;", (to_bigint(channel_id),))
        return bool(result.first()["count"])

    async def get_dvcs(self) -> AsyncGenerator[int, None]:
        """
        Get all dynamic voice channels.

        :return: An async generator of all dynamic voice channels.
        :rtype: AsyncGenerator[int, None]
        """
        result = await self.execute("SELECT id FROM feature_dvc;", paged=True)
        async for row in result:
            yield to_snowflake(row["id"])

    async def get_guild_dvcs(self, guild_id: int) -> AsyncGenerator[int, None]:
        """
        Get all dynamic voice channels in a guild.

        :param guild_id: The guild ID.
        :type guild_id: int

        :return: An async generator of all dynamic voice channels in the guild.
        :rtype: AsyncGenerator[int, None]
        """
        result = await self.execute(
            "SELECT id FROM feature_dvc WHERE guild_id = ? ALLOW FILTERING;", (to_bigint(guild_id),), paged=True
        )
        async for row in result:
            yield to_snowflake(row["id"])

    async def add_dvc(self, channel_id: int, owner_id: int, guild_id: int) -> None:
        """
        Add a dynamic voice channel.

        :param channel_id: The channel ID.
        :type channel_id: int
        :param owner_id: The owner ID.
        :type owner_id: int
        :param guild_id: The guild ID.
        :type guild_id: int
        """
        await self.execute(
            "INSERT INTO feature_dvc (id, owner_id, guild_id) VALUES (?, ?, ?);",
            (to_bigint(channel_id), to_bigint(owner_id), to_bigint(guild_id)),
        )

    async def remove_dvc(self, channel_id: int) -> None:
        """
        Remove a dynamic voice channel.

        :param channel_id: The channel ID.
        :type channel_id: int
        """
        await self.execute("DELETE FROM feature_dvc WHERE id = ?;", (to_bigint(channel_id),))

    async def get_guild_dvc_count(self, guild_id: int) -> int:
        """
        Get the number of dynamic voice channels in a guild.

        :param guild_id: The guild ID.
        :type guild_id: int

        :return: The number of dynamic voice channels in the guild.
        :rtype: int
        """
        result = await self.execute(
            "SELECT COUNT(*) FROM feature_dvc WHERE guild_id = ? ALLOW FILTERING;", (to_bigint(guild_id),)
        )
        return result.first()["count"]

    async def get_dvc_owner(self, channel_id: int) -> int:
        """
        Get the owner of a dynamic voice channel.

        :param channel_id: The channel ID.
        :type channel_id: int

        :return: The owner ID.
        :rtype: int
        """
        result = await self.execute("SELECT owner_id FROM feature_dvc WHERE id = ?;", (to_bigint(channel_id),))
        return to_snowflake(result.first()["owner_id"])

    async def set_dvc_owner(self, channel_id: int, owner_id: int) -> None:
        """
        Set the owner of a dynamic voice channel.

        :param channel_id: The channel ID.
        :type channel_id: int
        :param owner_id: The owner ID.
        :type owner_id: int
        """
        await self.execute(
            "UPDATE feature_dvc SET owner_id = ? WHERE id = ?;", (to_bigint(owner_id), to_bigint(channel_id))
        )

    async def get_guild_dvc_settings(self, guild_id: int) -> DvcSettingsModel:
        """
        Get the settings of the dynamic voice channels in a guild.

        :param guild_id: The guild ID.
        :type guild_id: int

        :return: The settings of the dynamic voice channels in the guild.
        :rtype: DvcSettingsModel
        """
        result = await self.execute("SELECT * FROM guild_dvc WHERE id = ?;", (to_bigint(guild_id),))
        return result.first(as_class=DvcSettingsModel) or DvcSettingsModel.default()

    async def set_guild_dvc_settings(self, guild_id: int, settings: DvcSettingsModel) -> None:
        """
        Set the settings of the dynamic voice channels in a guild.

        :param guild_id: The guild ID.
        :type guild_id: int
        :param settings: The settings of the dynamic voice channels.
        :type settings: DvcSettingsModel
        """
        await self.execute(
            "UPDATE guild_dvc SET enabled = ?, lobby = ?, name = ? WHERE id = ?;",
            (settings.enabled, to_bigint(settings.lobby), settings.name or "", to_bigint(guild_id)),
        )
