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

from ....const import PLACEHOLDER_EMOJI
from ....embed import Embed
from ..utils import return_option
from .fun import GuildFunSettings
from .general import DvcSettings, GuildGeneralSettings
from .preferences import GuildPreferencesSettings
from .safety import GuildSafetySettings, MessageSafetySettings

__all__ = (
    "GuildSettings",
    "GuildGeneralSettings",
    "GuildFunSettings",
    "GuildSafetySettings",
    "MessageSafetySettings",
    "GuildPreferencesSettings",
    "DvcSettings",
)


class GuildSettings:
    """
    This class contains methods to generate embed responses and components for the settings command.
    """

    @classmethod
    def embed(cls) -> Embed:
        """
        Create a guild settings embed.
        """
        return Embed(description="你可以在這裡修改這個伺服器的設定。")

    @staticmethod
    def components(ctx: interactions.ComponentContext) -> List[interactions.ActionRow]:
        """
        Generate components for the guild settings.

        :param ctx: The component context.
        :type ctx: interactions.ComponentContext

        :return: The components.
        :rtype: List[interactions.ActionRow]
        """
        return [
            interactions.ActionRow(
                interactions.StringSelectMenu(
                    interactions.StringSelectOption(
                        label="NekoOS • 伺服器設定",
                        value="placeholder",
                        emoji=PLACEHOLDER_EMOJI,
                        default=True,
                    ),
                    interactions.StringSelectOption(
                        label="一般功能設定",
                        value="general",
                        description="為伺服器配置各項功能 (如：動態語音頻道、歡迎訊息等)",
                        emoji="🔧",
                    ),
                    interactions.StringSelectOption(
                        label="趣味功能設定",
                        value="fun",
                        description="管理伺服器的趣味功能 (如：數數字等)",
                        emoji="🎮",
                    ),
                    interactions.StringSelectOption(
                        label="安全設定",
                        value="safety",
                        description="管理伺服器的安全設定 (如：訊息掃描、驗證等)",
                        emoji="🔒",
                    ),
                    interactions.StringSelectOption(
                        label="其他設定",
                        value="preferences",
                        description="修改伺服器的偏好設定 (如：語言 <- 未實裝)",
                        emoji="⚙️",
                    ),
                    return_option(),
                    custom_id="settings:guild_select",
                )
            )
        ]
