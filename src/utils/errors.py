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

from typing import Optional

__all__ = ("BotException", "Ratelimited")


class BotException(Exception):
    """The base exception for all exceptions raised by the bot."""


class Ratelimited(BotException):
    """
    This exception is raised when the client is ratelimited.
    """

    def __init__(self, message: str, retry_after: Optional[int] = None) -> None:
        super().__init__()
        self.message = message
        self.retry_after = retry_after
