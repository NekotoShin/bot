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

__all__ = (
    "REPLY_EMOJI",
    "PLACEHOLDER_EMOJI",
    "DISCORD_EPOCH",
)

REPLY_EMOJI = "<:reply:1252488534619852821>"

PLACEHOLDER_EMOJI = interactions.PartialEmoji(id=1250973097486712842)

DISCORD_EPOCH = 1420070400000
