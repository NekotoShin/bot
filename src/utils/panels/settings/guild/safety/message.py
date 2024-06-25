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

from .....const import PLACEHOLDER_EMOJI, SWITCH_OFF_EMOJI, SWITCH_ON_EMOJI
from .....embed import Embed
from ...utils import return_option

__all__ = ("MessageSafetySettings",)


class MessageSafetySettings:
    """
    This class contains methods to generate embed responses and components for the settings command.
    """

    @staticmethod
    def embed(safety: SafetySettingsModel, msg: str = None, success: bool = None) -> Embed:
        """
        Create a default dynamic voice channel settings embed.
        """
        emoji = SWITCH_ON_EMOJI.id if safety.enabled else SWITCH_OFF_EMOJI.id
        embed = Embed(msg or "這裡是訊息檢查的設定。", success)
        embed.set_thumbnail(f"https://cdn.discordapp.com/emojis/{emoji}.png")
        embed.add_field(
            name="Discord token檢查",
            value=f" 已{'啟用' if safety.dtoken else '停用'}",
            inline=True,
        )
        embed.add_field(
            name="連結安全掃描",
            value=f"已{'啟用' if safety.url else '停用'}",
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
                        label="NekoOS • 訊息檢查設定",
                        value="placeholder",
                        emoji=PLACEHOLDER_EMOJI,
                        default=True,
                    ),
                    interactions.StringSelectOption(
                        label="停用Discord token檢查" if safety.dtoken else "啟用Discord token檢查",
                        value="dtoken",
                        description=f"{'停止' if safety.dtoken else '開始'} 掃描訊息是否包含 Discord token",
                        emoji=SWITCH_OFF_EMOJI if safety.dtoken else SWITCH_ON_EMOJI,
                    ),
                    interactions.StringSelectOption(
                        label="停用連結安全掃描" if safety.url else "啟用連結安全掃描",
                        value="url",
                        description=f"{'停止' if safety.url else '開始'} 掃描訊息中的連結是否安全",
                        emoji=SWITCH_OFF_EMOJI if safety.url else SWITCH_ON_EMOJI,
                    ),
                    return_option(),
                    custom_id="safety_settings:message_select",
                ),
            ),
        ]
