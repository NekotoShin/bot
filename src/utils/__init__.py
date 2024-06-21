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

from .const import PLACEHOLDER_EMOJI, REPLY_EMOJI, URL_REGEX
from .discord import snowflake_time
from .embed import Embed
from .errors import BotException, Ratelimited
from .generators import DvcPanel, DvcSettings, Settings
from .validator import Validator

__all__ = (
    "Embed",
    "Settings",
    "DvcSettings",
    "DvcPanel",
    "snowflake_time",
    "REPLY_EMOJI",
    "PLACEHOLDER_EMOJI",
    "URL_REGEX",
    "BotException",
    "Ratelimited",
    "Validator",
)
