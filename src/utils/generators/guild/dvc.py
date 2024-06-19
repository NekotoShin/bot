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

from src.core.database.models import DvcSettings as DvcSettingsModel
from src.utils.embed import Embed

from ..core.settings import Settings

__all__ = ("DvcSettings",)


class DvcSettings:
    """
    This class contains methods to generate embed responses and components for the dynamic voice channel settings.
    """

    @staticmethod
    def embed(ctx: interactions.BaseContext, dvc: DvcSettingsModel, msg: str = None, success: bool = None) -> Embed:
        """
        Create a default dynamic voice channel settings embed.
        """
        emoji = 1252837291957682208 if dvc.enabled else 1252837290146005094
        embed = Embed(msg or "這裡是動態語音頻道的設定。", success)
        embed.set_thumbnail(f"https://cdn.discordapp.com/emojis/{emoji}.png")
        embed.add_field(
            name="目前狀態",
            value=f"<:reply:1252488534619852821> 動態語音已{'啟用' if dvc.enabled else '停用'}",
            inline=True,
        )
        if dvc.lobby == -1 or ctx.guild.get_channel(dvc.lobby) is None:
            value = "<:reply:1252488534619852821> 未設置"
        else:
            value = f"<:reply:1252488534619852821> <#{dvc.lobby}>"
        embed.add_field(name="大廳頻道", value=value, inline=True)
        embed.add_field(
            name="名稱格式",
            value=f"<:reply:1252488534619852821> {f'`{dvc.name}`' if dvc.name else '未設置'}",
        )
        return embed

    @staticmethod
    def components(dvc: DvcSettingsModel) -> List[interactions.ActionRow]:
        """
        Create components for the dynamic voice channel settings.
        """
        return [
            interactions.ActionRow(
                interactions.StringSelectMenu(
                    interactions.StringSelectOption(
                        label="NekoOS • 動態語音設定",
                        value="placeholder",
                        emoji=interactions.PartialEmoji(id=1250973097486712842),
                        default=True,
                    ),
                    interactions.StringSelectOption(
                        label="停用動態語音頻道" if dvc.enabled else "啟用動態語音頻道",
                        value="toggle",
                        description=f"{'停用' if dvc.enabled else '啟用'}動態語音頻道功能",
                        emoji=interactions.PartialEmoji(
                            id=1252837290146005094 if dvc.enabled else 1252837291957682208
                        ),
                    ),
                    interactions.StringSelectOption(
                        label="選擇頻道",
                        value="channel",
                        description="修改動態語音的大廳頻道",
                        emoji="🔊",
                    ),
                    interactions.StringSelectOption(
                        label="修改名稱",
                        value="name",
                        description="修改動態語音的名稱格式",
                        emoji="📝",
                    ),
                    Settings.return_option(),
                    custom_id="dvc_settings:select",
                ),
            ),
        ]

    @staticmethod
    def name_modal(current: str = None) -> interactions.Modal:
        """
        Create a modal for the dynamic voice channel name settings.
        """
        return interactions.Modal(
            interactions.InputText(
                label="名稱格式",
                style=interactions.TextStyles.SHORT,
                placeholder="請輸入希望使用的頻道名稱格式",
                value=current,
                custom_id="name",
                min_length=1,
                max_length=50,
            ),
            interactions.InputText(
                label="可用變數 (不用填寫這格)",
                style=interactions.TextStyles.PARAGRAPH,
                placeholder="""{{count}} - 動態語音頻道編號
{{user}} - 創建者的顯示名稱
{{username}} - 創建者的用戶名稱
{{id}} - 創建者的ID
{{guild}} - 伺服器名稱""",
                required=False,
            ),
            title="動態語音頻道 - 名稱格式",
            custom_id="dvc_settings:name",
        )

    @staticmethod
    def channel_embed() -> Embed:
        """
        Create an embed for the dynamic voice channel channel settings.
        """
        return Embed("請選擇一個動態語音大廳頻道。")

    @staticmethod
    def channel_components() -> List[interactions.ActionRow]:
        """
        Create components for the dynamic voice channel channel settings.
        """
        return [
            interactions.ActionRow(
                interactions.ChannelSelectMenu(
                    channel_types=[interactions.ChannelType.GUILD_VOICE],
                    custom_id="dvc_settings:channel_select",
                    placeholder="🔊｜請選擇一個語音頻道",
                )
            ),
            interactions.ActionRow(
                interactions.StringSelectMenu(
                    interactions.StringSelectOption(
                        label="NekoOS • 大廳頻道",
                        value="placeholder",
                        emoji=interactions.PartialEmoji(id=1250973097486712842),
                        default=True,
                    ),
                    Settings.return_option(),
                    custom_id="dvc_settings:channel_action_select",
                ),
            ),
        ]
