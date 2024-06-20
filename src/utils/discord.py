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

import interactions

from .const import DISCORD_EPOCH

__all__ = ("snowflake_time",)


def snowflake_time(snowflake: interactions.Snowflake_Type) -> int:
    """
    Get the timestamp of a Discord snowflake.

    :param snowflake: The snowflake.
    :type snowflake: Snowflake_Type

    :return: The timestamp.
    :rtype: int
    """
    return ((int(snowflake) >> 22) + DISCORD_EPOCH) / 1000
