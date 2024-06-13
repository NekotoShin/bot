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

import copy
import glob
import logging
import os
from typing import Union

import interactions
import psutil
from interactions.ext import prefixed_commands
from scyllapy.exceptions import ScyllaPyDBError

from src.core import Config, Database, InterceptHandler, Logger


class Client(interactions.Client):
    """
    The modified discord bot client.
    """

    __version__ = "0.0.1"
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Client, cls).__new__(cls, *args, **kwargs)
        else:
            raise RuntimeError("Client is already initialized. Only one instance of the client is allowed.")
        return cls._instance

    def __init__(self) -> None:
        # load the configuration files
        self.config = Config("config/global.toml")

        # setup the logger
        if self.config["logging"]["level"] not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError("Invalid logging level. Must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL.")

        self.logger = Logger(
            log_format=self.config["logging"]["format"],
            level=self.config["logging"]["level"],
            retention=self.config["logging"]["retention"],
        )
        logging.basicConfig(
            handlers=[InterceptHandler(self.logger)],
            level=logging._nameToLevel[self.config["logging"]["level"]],
            force=True,
        )

        # prepare the database instance
        self.database = Database(
            hosts=self.config["database"]["hosts"],
            username=self.config["database"]["username"],
            password=self.config["database"]["password"],
            keyspace=self.config["database"]["keyspace"],
        )

        # initialize the client
        super().__init__(
            intents=interactions.Intents.ALL & ~interactions.Intents.GUILD_PRESENCES,
            owner_ids=self.config["bot"]["developers"],
            fetch_members=True,
            logger=self.logger,
        )
        prefixed_commands.setup(self, generate_prefixes=prefixed_commands.when_mentioned_or("!"))

        # load extensions
        for i in glob.glob("src/exts/**/*.py", recursive=True):
            if i.endswith("template.py") or i.endswith("__init__.py"):
                continue
            self.load_extension(i.removesuffix(".py").replace("/", "."))

    @interactions.listen()
    async def on_startup(self) -> None:
        """
        The event that is triggered when the bot is started.
        """
        try:
            await self.database.initialize()
        except ScyllaPyDBError:
            self.logger.critical_exc("Failed to initialize the database.")
            return await self.stop()
        else:
            self.logger.info("Database connection established.")
        self.logger.info(
            "\n-------------------------"
            "\nLogged in as: {}#{} ({})"
            "\nShards Count: {}"
            "\nMemory Usage: {:.2f} MB"
            "\n-------------------------",
            self.user.username,
            self.user.discriminator,
            self.user.id,
            self.total_shards,
            psutil.Process(os.getpid()).memory_info().rss / (1024**2),
        )

    def get_invite_url(self, permissions: Union[int, interactions.Permissions]) -> str:
        """
        Gets the invite URL for the bot.

        :param p: The permissions to use.
        :type p: Union[int, discord.Permissions]

        :return: The invite URL.
        :rtype: str
        """
        if isinstance(permissions, interactions.Permissions):
            permissions = permissions.value
        return f"https://discord.com/oauth2/authorize?client_id={self.user.id}" f"&scope=bot&permissions={permissions}"

    @staticmethod
    def has_permissions(has: interactions.Permissions, *required: Union[interactions.Permissions, int]) -> bool:
        """
        Check if a permission set has the required permissions.

        :param has: The permission set to check.
        :type has: interactions.Permissions
        :param required: The required permissions or integer values representing permissions.
        :type required: Tuple[interactions.Permissions, int]

        :return: Whether the permission set has the required permissions.
        :rtype: bool
        """
        r = interactions.Permissions(0)
        for p in required:
            if isinstance(p, int):
                p = interactions.Permissions(p)
            r |= p
        return (has & r) == r

    async def wait_until_ready(self) -> None:
        await self.database.wait_until_ready()
        return await super().wait_until_ready()

    async def stop(self) -> None:
        """
        Stops the bot and closes the database connection gracefully.
        """
        self.logger.info("Shutting down...")
        await self.database.close()
        await super().stop()

    async def get_context(self, data: dict) -> interactions.InteractionContext:
        """
        Get the context for the interaction.

        This is called when any interaction is received.
        Overriden the original get_context method to properly resolve the default values for the select menus.
        This is required until the interactions-py/interactions.py dev team implements a fix.
        Issue (i.py discord server): https://discord.com/channels/789032594456576001/1245552000909836399

        :data: The data for the interaction.
        :type data: dict

        :return: The interaction context.
        :rtype: interactions.InteractionContext
        """
        temp = copy.deepcopy(data)

        cls = await super().get_context(data)
        if temp["type"] == interactions.InteractionType.MESSAGE_COMPONENT:
            for i, row in enumerate(temp["message"]["components"]):
                for j, component in enumerate(row["components"]):
                    if component["type"] in (
                        interactions.ComponentType.USER_SELECT,
                        interactions.ComponentType.MENTIONABLE_SELECT,
                        interactions.ComponentType.CHANNEL_SELECT,
                        interactions.ComponentType.ROLE_SELECT,
                    ):
                        values = []
                        if "default_values" in component:
                            searches = {
                                "users": component["type"]
                                in (
                                    interactions.ComponentType.USER_SELECT,
                                    interactions.ComponentType.MENTIONABLE_SELECT,
                                ),
                                "members": temp["guild_id"]
                                and component["type"]
                                in (
                                    interactions.ComponentType.USER_SELECT,
                                    interactions.ComponentType.MENTIONABLE_SELECT,
                                ),
                                "channels": component["type"]
                                in (
                                    interactions.ComponentType.CHANNEL_SELECT,
                                    interactions.ComponentType.MENTIONABLE_SELECT,
                                ),
                                "roles": temp["guild_id"]
                                and component["type"]
                                in (
                                    interactions.ComponentType.ROLE_SELECT,
                                    interactions.ComponentType.MENTIONABLE_SELECT,
                                ),
                            }
                            for value in component["default_values"]:
                                key = interactions.Snowflake(value["id"])
                                if resolved := cls.resolved.get(key):
                                    values.append(resolved)
                                elif searches["users"] and (user := self.cache.get_user(key)):
                                    values.append(user)
                                elif searches["members"] and (member := self.cache.get_member(temp["guild_id"], key)):
                                    values.append(member)
                                elif searches["channels"] and (channel := self.cache.get_channel(key)):
                                    values.append(channel)
                                elif searches["roles"] and (role := self.cache.get_role(key)):
                                    values.append(role)
                        cls.message.components[i].components[j].default_values = values
        return cls


class BaseExtension(interactions.Extension):
    """
    The base extension class.
    Always inherit from this class when creating a new extension.
    """

    def __init__(self, client: Client) -> None:
        self.client = client
        self.logger.info(f"Loaded extension {self.__class__.__name__}.")

    def drop(self) -> None:
        self.logger.info(f"Unloaded extension {self.__class__.__name__}.")
        return super().drop()

    @property
    def logger(self) -> Logger:
        return self.client.logger

    @property
    def global_config(self) -> Config:
        return self.client.config

    @property
    def database(self) -> Database:
        return self.client.database
