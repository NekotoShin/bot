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

from interactions import Snowflake_Type
from scyllapy.extra_types import BigInt


def to_bigint(snowflake: Snowflake_Type) -> BigInt:
    """
    Convert a snowflake (uint64) to a bigint.

    :param snowflake: The snowflake to convert.
    :type snowflake: Snowflake_Type

    :return: The bigint representation of the snowflake.
    :rtype: BigInt
    """
    return BigInt(int(snowflake) - 9223372036854775808)


def to_snowflake(bigint: BigInt) -> int:
    """
    Convert a bigint to a snowflake.
    Revert the conversion done by to_bigint.

    :param bigint: The bigint to convert.
    :type bigint: BigInt

    :return: The snowflake of which the bigint was converted from.
    :rtype: int
    """
    return bigint + 9223372036854775808
