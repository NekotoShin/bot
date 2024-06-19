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

from src.utils.embed import Embed

__all__ = ("Settings",)


class Settings:
    """
    This class contains methods to generate embed responses and components for the settings command.
    """

    @staticmethod
    def return_option() -> interactions.StringSelectOption:
        """
        Generate a return option for the settings command.

        :return: The return option.
        :rtype: interactions.StringSelectOption
        """
        return interactions.StringSelectOption(
            label="返回",
            value="return",
            description="回到上一個選單",
            emoji="🔙",
        )

    @classmethod
    def default_embed(cls) -> Embed:
        """
        Create a default settings embed.
        """
        return Embed("你可以在這裡設定機器人的各種功能或個人化選項。")

    @staticmethod
    def default_components(ctx: interactions.BaseContext) -> List[interactions.ActionRow]:
        """
        Generate components for the settings command.

        :param ctx: The context.
        :type ctx: interactions.BaseContext

        :return: The components.
        :rtype: List[interactions.ActionRow]
        """
        options = [
            interactions.StringSelectOption(
                label="NekoOS • 系統設定",
                value="placeholder",
                emoji=interactions.PartialEmoji(id=1250973097486712842),
                default=True,
            ),
        ]
        if ctx.guild:
            options.append(
                interactions.StringSelectOption(
                    label="伺服器設定", value="guild", description="管理伺服器的設定選項", emoji="🛠️"
                )
            )
        options.append(
            interactions.StringSelectOption(
                label="個人化選項", value="personal", description="修改你的專屬設定", emoji="👤"
            )
        )
        return [
            interactions.ActionRow(
                interactions.StringSelectMenu(
                    *options,
                    custom_id="settings:type_select",
                ),
            ),
        ]

    @classmethod
    def guild_embed(cls) -> Embed:
        """
        Create a guild settings embed.
        """
        return Embed(description="你可以在這裡修改這個伺服器的設定。")

    @staticmethod
    def guild_components(ctx: interactions.ComponentContext) -> List[interactions.ActionRow]:
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
                        emoji=interactions.PartialEmoji(id=1250973097486712842),
                        default=True,
                    ),
                    interactions.StringSelectOption(
                        label="功能設定",
                        value="features",
                        description="為伺服器配置各項功能 (如：動態語音頻道、歡迎訊息等)",
                        emoji="🔧",
                    ),
                    interactions.StringSelectOption(
                        label="偏好設定",
                        value="preferences",
                        description="修改伺服器的偏好設定 (如：語言 <- 未實裝)",
                        emoji="⚙️",
                    ),
                    Settings.return_option(),
                    custom_id="settings:guild_select",
                )
            )
        ]

    @classmethod
    def features_embed(cls) -> Embed:
        """
        Create a features settings embed.
        """
        return Embed(description="你可以在這裡為這個伺服器設定各種功能。")

    @staticmethod
    def features_components(ctx: interactions.ComponentContext) -> List[interactions.ActionRow]:
        """
        Generate components for the features settings.

        :param ctx: The component context.
        :type ctx: interactions.ComponentContext

        :return: The components.
        :rtype: List[interactions.ActionRow]
        """
        options = [
            interactions.StringSelectOption(
                label="NekoOS • 伺服器功能設定",
                value="placeholder",
                emoji=interactions.PartialEmoji(id=1250973097486712842),
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
                    Settings.return_option(),
                    custom_id="settings:features_select",
                )
            )
        ]

    @classmethod
    def preferences_embed(cls) -> Embed:
        """
        Create a preferences settings embed.
        """
        return Embed(description="你可以在這裡修改這個伺服器的偏好設定。")

    @staticmethod
    def preferences_components(ctx: interactions.ComponentContext) -> List[interactions.ActionRow]:
        """
        Generate components for the preferences settings.

        :param ctx: The component context.
        :type ctx: interactions.ComponentContext

        :return: The components.
        :rtype: List[interactions.ActionRow]
        """
        return [
            interactions.ActionRow(
                interactions.StringSelectMenu(
                    interactions.StringSelectOption(
                        label="NekoOS • 伺服器偏好設定",
                        value="placeholder",
                        emoji=interactions.PartialEmoji(id=1250973097486712842),
                        default=True,
                    ),
                    Settings.return_option(),
                    custom_id="settings:preferences_select",
                )
            )
        ]

    @classmethod
    def personal_embed(cls) -> Embed:
        """
        Create a personal settings embed.
        """
        return Embed(description="你可以在這裡修改專屬於你的個人化選項。")

    @staticmethod
    def personal_components(ctx: interactions.ComponentContext) -> List[interactions.ActionRow]:
        """
        Generate components for the personal settings.

        :param ctx: The component context.
        :type ctx: interactions.ComponentContext

        :return: The components.
        :rtype: List[interactions.ActionRow]
        """
        options = [
            interactions.StringSelectOption(
                label="NekoOS • 個人化選項",
                value="placeholder",
                emoji=interactions.PartialEmoji(id=1250973097486712842),
                default=True,
            ),
        ]
        return [
            interactions.ActionRow(
                interactions.StringSelectMenu(
                    *options,
                    Settings.return_option(),
                    custom_id="settings:personal_select",
                )
            )
        ]
