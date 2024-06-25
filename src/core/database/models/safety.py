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

from scyllapy.extra_types import ScyllaPyUDT


@dataclasses.dataclass
class SafetySettings(ScyllaPyUDT):
    """
    A User-Defined Type (UDT) dataclass representing the safety settings of a guild.
    This class corresponds to the `safetySettings` UDT in the database.
    """

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
    def default(cls) -> "SafetySettings":
        """
        Create a new SafetySettings instance with default values.

        :return: The created SafetySettings instance.
        :rtype: SafetySettings
        """
        return cls(dtoken=True, url=True)
