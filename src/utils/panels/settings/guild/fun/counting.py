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

from src.core.database import CountingSettingsModel
from src.utils.embed import Embed

from .....const import PLACEHOLDER_EMOJI, SWITCH_OFF_EMOJI, SWITCH_ON_EMOJI
from ...utils import return_option

__all__ = ("CountingSettings",)


class CountingSettings:
    """
    This class contains methods to generate embed responses and components for the counting game settings.
    """

    @staticmethod
    def embed(
        ctx: interactions.BaseContext, counting: CountingSettingsModel, msg: str = None, success: bool = None
    ) -> Embed:
        """
        Create a default dynamic voice channel settings embed.
        """
        emoji = SWITCH_ON_EMOJI.id if counting.enabled else SWITCH_OFF_EMOJI.id
        embed = Embed(msg or "這裡是數數字遊戲的設定。", success)
        embed.set_thumbnail(f"https://cdn.discordapp.com/emojis/{emoji}.png")
        channel_set = counting.channel != -1 and ctx.guild.get_channel(counting.channel) is not None
        embed.add_field(
            name="目前狀態",
            value=f"已{'啟用' if counting.enabled and channel_set else '停用'}",
            inline=True,
        )
        embed.add_field(
            name="遊戲頻道",
            value=f"<#{counting.channel}>" if channel_set else "未設置",
            inline=True,
        )
        return embed

    @staticmethod
    def components(counting: CountingSettingsModel) -> List[interactions.ActionRow]:
        """
        Create components for the dynamic voice channel settings.
        """
        return [
            interactions.ActionRow(
                interactions.StringSelectMenu(
                    interactions.StringSelectOption(
                        label="NekoOS • 數數字設定",
                        value="placeholder",
                        emoji=PLACEHOLDER_EMOJI,
                        default=True,
                    ),
                    interactions.StringSelectOption(
                        label="停用數數字遊戲" if counting.enabled else "啟用數數字遊戲",
                        value="toggle",
                        description=f"{'停用' if counting.enabled else '啟用'}數數字遊戲的功能",
                        emoji=SWITCH_OFF_EMOJI if counting.enabled else SWITCH_ON_EMOJI,
                    ),
                    interactions.StringSelectOption(
                        label="選擇頻道",
                        value="channel",
                        description="修改數數字遊戲的頻道",
                        emoji="🔊",
                    ),
                    return_option(),
                    custom_id="counting_settings:select",
                ),
            ),
        ]

    @staticmethod
    def channel_embed() -> Embed:
        """
        Create an embed for the counting channel settings.
        """
        return Embed("請選擇一個文字頻道作為數數字遊戲的頻道。")

    @staticmethod
    def channel_components() -> List[interactions.ActionRow]:
        """
        Create components for the counting channel settings.
        """
        return [
            interactions.ActionRow(
                interactions.ChannelSelectMenu(
                    channel_types=[interactions.ChannelType.GUILD_TEXT],
                    custom_id="counting_settings:channel_select",
                    placeholder="💬｜請選擇一個文字頻道",
                )
            ),
            interactions.ActionRow(
                interactions.StringSelectMenu(
                    interactions.StringSelectOption(
                        label="NekoOS • 數數字頻道",
                        value="placeholder",
                        emoji=PLACEHOLDER_EMOJI,
                        default=True,
                    ),
                    return_option(),
                    custom_id="counting_settings:channel_action_select",
                ),
            ),
        ]
