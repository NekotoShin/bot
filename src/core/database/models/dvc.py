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
from typing import Any, List

from scyllapy.extra_types import ScyllaPyUDT

from ..utils import to_bigint, to_snowflake


@dataclasses.dataclass
class DvcSettings(ScyllaPyUDT):
    """
    A User-Defined Type (UDT) dataclass representing the settings of a dynamic voice channel.
    This class corresponds to the `dvcSettings` UDT in the database.
    """

    enabled: bool
    lobby: int
    name: str

    def __post_init__(self):
        self.lobby = -1 if self.lobby is None else to_snowflake(self.lobby)

    def __dump_udt__(self) -> List[Any]:
        self.lobby = to_bigint(self.lobby) if self.lobby != -1 else None
        self.name = self.name or ""
        return super().__dump_udt__()

    @classmethod
    def create(cls, enabled: bool, lobby: int, name: str) -> "DvcSettings":
        """
        Create a new DvcSettings instance to be inserted into the database.

        :param enabled: Whether the dynamic voice channels are enabled.
        :type enabled: bool
        :param lobby: The ID of the lobby channel.
        :type lobby: int
        :param name: The name of the dynamic voice channel.
        :type name: str

        :return: The created DvcSettings instance.
        :rtype: DvcSettings
        """
        return cls(enabled=enabled, lobby=None if lobby is None else to_bigint(lobby, True), name=name)

    @classmethod
    def default(cls) -> "DvcSettings":
        """
        Create a new DvcSettings instance with default values.

        :return: The created DvcSettings instance.
        :rtype: DvcSettings
        """
        return cls(enabled=False, lobby=to_bigint(-1, True), name=None)
