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

from .....const import PLACEHOLDER_EMOJI
from .....embed import Embed
from ...utils import return_option
from .dvc import DvcSettings

__all__ = ("GuildGeneralSettings", "DvcSettings")


class GuildGeneralSettings:
    """
    This class contains methods to generate embed responses and components for the settings command.
    """

    @classmethod
    def embed(cls) -> Embed:
        """
        Create a general settings embed.
        """
        return Embed(description="你可以在這裡為這個伺服器設定各種功能。")

    @staticmethod
    def components(ctx: interactions.ComponentContext) -> List[interactions.ActionRow]:
        """
        Generate components for the general settings.

        :param ctx: The component context.
        :type ctx: interactions.ComponentContext

        :return: The components.
        :rtype: List[interactions.ActionRow]
        """
        options = [
            interactions.StringSelectOption(
                label="NekoOS • 一般功能設定",
                value="placeholder",
                emoji=PLACEHOLDER_EMOJI,
                default=True,
            ),
        ]
        if ctx.author.has_permission(interactions.Permissions.MANAGE_CHANNELS):
            options.append(
                interactions.StringSelectOption(
                    label="動態語音頻道",
                    value="dvc",
                    description="管理動態語音頻道的設定",
                    emoji="🔊",
                )
            )
        return [
            interactions.ActionRow(
                interactions.StringSelectMenu(
                    *options,
                    return_option(),
                    custom_id="settings:general_select",
                )
            )
        ]
