"""
The database module of the bot.
"""

import asyncio
from typing import List, Optional

from scyllapy import Consistency, ExecutionProfile, Scylla

__all__ = ("Database",)


class Database:
    """
    The database class of the bot.
    """

    _ready = asyncio.Event()
    _profile = ExecutionProfile(consistency=Consistency.ALL)

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

        # create types

        # create tables

        # set ready flag
        self._ready.set()

    async def close(self) -> None:
        """
        Closes the database connection.
        """
        if self._ready.is_set():
            await self.scylla.shutdown()
