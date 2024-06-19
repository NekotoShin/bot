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
from typing import Any, Dict, Iterable, List, Optional, Union

from scyllapy import Consistency, ExecutionProfile, Scylla

__all__ = ("DatabaseCore",)


class Queries:
    """
    The class for storing queries.
    """

    def __init__(self) -> None:
        self.queries = []

    def add(self, query: str, params: Optional[Union[Iterable[Any], Dict[str, Any]]] = None) -> None:
        """
        Adds a query to the list.
        """
        self.queries.append((query, params))

    async def execute(self, scylla: Scylla) -> None:
        """
        Executes the queries.
        """
        for query, params in self.queries:
            await scylla.execute(query, params)
        self.queries.clear()


class DatabaseCore:
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
        self.type_queries = Queries()
        self.table_queries = Queries()

    # Connection

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
        await self.type_queries.execute(self.scylla)
        await self.table_queries.execute(self.scylla)
        self._ready.set()

    async def close(self) -> None:
        """
        Closes the database connection.
        """
        if self._ready.is_set():
            await self.scylla.shutdown()


class FeatureDatabase:
    """
    The database class for each features.
    """

    def __init__(self, core: DatabaseCore) -> None:
        self.core = core

    async def execute(self, *args, **kwargs):
        """
        Executes a query.
        """
        return await self.core.scylla.execute(*args, **kwargs)

    async def wait_until_ready(self) -> None:
        """
        Waits until the database is ready.
        """
        await self.core.wait_until_ready()
