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
