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

from src.core.database import SettingsDatabase
from src.main import BaseExtension, Client
from src.utils import DvcSettings, Settings


class SettingsExt(BaseExtension):
    """
    The extension class for the settings commands.
    """

    def __init__(self, client: Client):
        """
        The constructor for the extension.

        :param client: The client object.
        :type client: Client
        """
        super().__init__(client=client)
        self.database: SettingsDatabase = self.feature_database["settings"]

    @interactions.slash_command(name=interactions.LocalizedName(english_us="settings", chinese_taiwan="設定"))
    @interactions.integration_types(guild=True, user=True)
    async def settings(self, ctx: interactions.SlashContext):
        """管理機器人設定"""
        await ctx.defer(ephemeral=True)
        await ctx.respond(embed=Settings.default_embed(), components=Settings.default_components(ctx))

    @interactions.component_callback("settings:type_select")
    async def type_select(self, ctx: interactions.ComponentContext):
        """
        The component callback for the type select menu.
        """
        await ctx.defer(edit_origin=True)
        option = ctx.values[0]
        if option == "guild":
            embed = Settings.guild_embed()
            components = Settings.guild_components(ctx)
        elif option == "personal":
            embed = Settings.personal_embed()
            components = Settings.personal_components(ctx)
        elif option == "placeholder":
            embed, components = None, None
        await ctx.edit_origin(embed=embed, components=components)

    @interactions.component_callback("settings:guild_select")
    async def guild_select(self, ctx: interactions.ComponentContext):
        """
        The component callback for the guild select menu.
        """
        await ctx.defer(edit_origin=True)
        option = ctx.values[0]
        if option == "features":
            embed = Settings.features_embed()
            components = Settings.features_components(ctx)
        elif option == "placeholder":
            embed, components = None, None
        elif option == "preferences":
            embed = Settings.preferences_embed()
            components = Settings.preferences_components(ctx)
        elif option == "return":
            embed = Settings.default_embed()
            components = Settings.default_components(ctx)
        await ctx.edit_origin(embed=embed, components=components)

    @interactions.component_callback("settings:personal_select")
    async def personal_select(self, ctx: interactions.ComponentContext):
        """
        The component callback for the personal select menu.
        """
        await ctx.defer(edit_origin=True)
        option = ctx.values[0]
        if option == "placeholder":
            embed, components = None, None
        elif option == "return":
            embed = Settings.default_embed()
            components = Settings.default_components(ctx)
        await ctx.edit_origin(embed=embed, components=components)

    @interactions.component_callback("settings:features_select")
    async def features_select(self, ctx: interactions.ComponentContext):
        """
        The component callback for the features select menu.
        """
        await ctx.defer(edit_origin=True)
        option = ctx.values[0]
        if option == "dvc":
            dvc = await self.feature_database["dvc"].get_guild_dvc_settings(ctx.guild.id)
            embed = DvcSettings.embed(ctx, dvc)
            components = DvcSettings.components(ctx, dvc)
        elif option == "placeholder":
            embed, components = None, None
        elif option == "return":
            embed = Settings.guild_embed()
            components = Settings.guild_components(ctx)
        await ctx.edit_origin(embed=embed, components=components)

    @interactions.component_callback("settings:preferences_select")
    async def preferences_select(self, ctx: interactions.ComponentContext):
        """
        The component callback for the preferences select menu.
        """
        await ctx.defer(edit_origin=True)
        option = ctx.values[0]
        if option == "placeholder":
            embed, components = None, None
        elif option == "return":
            embed = Settings.guild_embed()
            components = Settings.guild_components(ctx)
        await ctx.edit_origin(embed=embed, components=components)


def setup(client: Client):
    """
    The setup function for the extension.

    :param client: The client object.
    :type client: Client
    """
    SettingsExt(client)
