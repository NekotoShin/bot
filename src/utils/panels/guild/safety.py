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

from typing import List

import interactions

from src.core.database.models import SafetySettings as SafetySettingsModel
from src.utils.embed import Embed

from ...const import PLACEHOLDER_EMOJI
from ..core import Settings

__all__ = ("SafetySettings",)


class SafetySettings:
    """
    This class contains methods to generate embed responses and components for the dynamic voice channel settings.
    """

    @staticmethod
    def embed(safety: SafetySettingsModel, msg: str = None, success: bool = None) -> Embed:
        """
        Create a default dynamic voice channel settings embed.
        """
        emoji = 1252837291957682208 if safety.enabled else 1252837290146005094
        embed = Embed(msg or "這裡是安全檢查的設定。", success)
        embed.set_thumbnail(f"https://cdn.discordapp.com/emojis/{emoji}.png")
        embed.add_field(
            name="目前狀態 - 訊息檢查",
            value=f"Discord token檢查已{'啟用' if safety.dtoken else '停用'}\n連結安全掃描已{'啟用' if safety.url else '停用'}",
            inline=True,
        )
        return embed

    @staticmethod
    def components(safety: SafetySettingsModel) -> List[interactions.ActionRow]:
        """
        Create components for the dynamic voice channel settings.
        """
        return [
            interactions.ActionRow(
                interactions.StringSelectMenu(
                    interactions.StringSelectOption(
                        label="NekoOS • 安全檢查設定",
                        value="placeholder",
                        emoji=PLACEHOLDER_EMOJI,
                        default=True,
                    ),
                    interactions.StringSelectOption(
                        label="停用Discord token檢查" if safety.dtoken else "啟用Discord token檢查",
                        value="dtoken",
                        description=f"{'停用' if safety.dtoken else '啟用'}訊息檢查 (Discord token)",
                        emoji=interactions.PartialEmoji(
                            id=1252837290146005094 if safety.dtoken else 1252837291957682208
                        ),
                    ),
                    interactions.StringSelectOption(
                        label="停用連結安全掃描" if safety.url else "啟用連結安全掃描",
                        value="url",
                        description=f"{'停用' if safety.url else '啟用'}訊息檢查 (連結安全掃描)",
                        emoji=interactions.PartialEmoji(id=1252837290146005094 if safety.url else 1252837291957682208),
                    ),
                    Settings.return_option(),
                    custom_id="safety_settings:select",
                ),
            ),
        ]
