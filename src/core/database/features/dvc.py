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

from typing import AsyncGenerator

from ..core import DatabaseCore, FeatureDatabase
from ..models import DvcSettings
from ..utils import to_bigint, to_snowflake

__all__ = ("DvcDatabase",)


class DvcDatabase(FeatureDatabase):
    """
    The database class of the bot.
    """

    def __init__(self, core: DatabaseCore) -> None:
        super().__init__(core)
        self.core.type_queries.add(
            """
            CREATE TYPE IF NOT EXISTS dvcSettings (
                enabled BOOLEAN,
                lobby BIGINT,
                name TEXT,
            )
            """
        )
        self.core.table_queries.add(
            """
            CREATE TABLE IF NOT EXISTS dvc (
                id BIGINT,
                owner_id BIGINT,
                guild_id BIGINT,
                PRIMARY KEY (id)
            );
            """
        )
        self.core.table_queries.add("CREATE INDEX IF NOT EXISTS ON dvc (guild_id);")

    async def is_dvc(self, channel_id: int) -> bool:
        """
        Checks if a channel is a dynamic voice channel.

        :param channel_id: The channel ID.
        :type channel_id: int

        :return: Whether the channel is a dynamic voice channel.
        :rtype: bool
        """
        result = await self.execute("SELECT COUNT(*) FROM dvc WHERE id = ?;", (to_bigint(channel_id),))
        return bool(result.first()["count"])

    async def get_dvcs(self) -> AsyncGenerator[int, None]:
        """
        Get all dynamic voice channels.

        :return: An async generator of all dynamic voice channels.
        :rtype: AsyncGenerator[int, None]
        """
        result = await self.execute("SELECT id FROM dvc;", paged=True)
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
            "INSERT INTO dvc (id, owner_id, guild_id) VALUES (?, ?, ?);",
            (to_bigint(channel_id), to_bigint(owner_id), to_bigint(guild_id)),
        )

    async def remove_dvc(self, channel_id: int) -> None:
        """
        Remove a dynamic voice channel.

        :param channel_id: The channel ID.
        :type channel_id: int
        """
        await self.execute("DELETE FROM dvc WHERE id = ?;", (to_bigint(channel_id),))

    async def get_dvc_count(self, guild_id: int) -> int:
        """
        Get the number of dynamic voice channels in a guild.

        :param guild_id: The guild ID.
        :type guild_id: int

        :return: The number of dynamic voice channels in the guild.
        :rtype: int
        """
        result = await self.execute("SELECT COUNT(*) FROM dvc WHERE guild_id = ?;", (to_bigint(guild_id),))
        return result.first()["count"]

    async def get_dvc_owner(self, channel_id: int) -> int:
        """
        Get the owner of a dynamic voice channel.

        :param channel_id: The channel ID.
        :type channel_id: int

        :return: The owner ID.
        :rtype: int
        """
        result = await self.execute("SELECT owner_id FROM dvc WHERE id = ?;", (to_bigint(channel_id),))
        return to_snowflake(result.first()["owner_id"])

    async def set_dvc_owner(self, channel_id: int, owner_id: int) -> None:
        """
        Set the owner of a dynamic voice channel.

        :param channel_id: The channel ID.
        :type channel_id: int
        :param owner_id: The owner ID.
        :type owner_id: int
        """
        await self.execute("UPDATE dvc SET owner_id = ? WHERE id = ?;", (to_bigint(owner_id), to_bigint(channel_id)))

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
