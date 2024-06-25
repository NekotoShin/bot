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

import asyncio
from typing import List, Optional

from scyllapy import Consistency, ExecutionProfile, Scylla

from .features import Dvc, GuildSettings

__all__ = ("DatabaseClient",)


class DatabaseClient(Dvc, GuildSettings):
    """
    The database class of the bot.
    """

    _ready = asyncio.Event()
    _profile = ExecutionProfile(consistency=Consistency.QUORUM)

    def __init__(
        self,
        hosts: List[str],
        username: Optional[str] = "",
        password: Optional[str] = "",
        keyspace: Optional[str] = "discord",
        **kwargs
    ) -> None:
        self.scylla = Scylla(
            contact_points=hosts,
            username=username,
            password=password,
            keyspace=keyspace,
            default_execution_profile=self._profile,
            **kwargs
        )

    async def wait_until_ready(self) -> None:
        """
        Waits until the database is ready.
        """
        await self._ready.wait()

    async def initialize(self) -> None:
        """
        Initializes the database.
        """
        await self.scylla.startup()
        await self.setup_udts()
        await self.setup_tables()
        self._ready.set()

    async def setup_udts(self) -> None:
        """
        Sets up the user-defined types.
        """
        await self.scylla.execute(
            """
            CREATE TYPE IF NOT EXISTS dvcSettings (
                enabled BOOLEAN,
                lobby BIGINT,
                name TEXT,
            );
            """
        )
        await self.scylla.execute(
            """
            CREATE TYPE IF NOT EXISTS safetySettings (
                dtoken BOOLEAN,
                url BOOLEAN,
            );
            """
        )

    async def setup_tables(self) -> None:
        """
        Sets up the tables.
        """
        await self.scylla.execute(
            """
            CREATE TABLE IF NOT EXISTS dvc (
                id BIGINT,
                owner_id BIGINT,
                guild_id BIGINT,
                PRIMARY KEY (id)
            );
            """
        )
        await self.scylla.execute(
            """
            CREATE TABLE IF NOT EXISTS guilds (
                id BIGINT,
                dvc frozen<dvcSettings>,
                safety frozen<safetySettings>,
                PRIMARY KEY (id)
            );
            """
        )

    async def execute(self, *args, **kwargs) -> None:
        """
        Executes a query.
        """
        await self.wait_until_ready()
        return await self.scylla.execute(*args, **kwargs)

    async def close(self) -> None:
        """
        Closes the database connection.
        """
        if self._ready.is_set():
            await self.scylla.shutdown()
