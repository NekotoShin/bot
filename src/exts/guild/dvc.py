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

import asyncio
from typing import List, Tuple

import interactions  # noqa: F401
from interactions.api.events import VoiceStateUpdate

from src.core.database import DvcDatabase, models
from src.main import BaseExtension, Client
from src.utils import DvcSettings, Embed, Settings


class DvcExtension(BaseExtension):
    """
    The base extension class for the dynamic voice channels.
    """

    def __init__(self, client: Client):
        """
        The constructor for the extension.

        :param client: The client object.
        :type client: Client
        """
        super().__init__(client=client)
        self.database: DvcDatabase = self.feature_database["dvc"]


class DvcModals(DvcExtension):
    """
    The extension class for the dynamic voice channel modals.
    """

    @interactions.modal_callback("dvc_settings:name")
    async def name_modal(self, ctx: interactions.ModalContext, name: str, **_):
        """
        The modal callback for the dynamic voice channel name modal.
        """
        await ctx.defer(edit_origin=True)
        dvc = await self.database.get_guild_dvc_settings(ctx.guild.id)
        if name := name.strip():
            dvc.name = name
            await self.database.set_guild_dvc_settings(ctx.guild.id, models.DvcSettings.create(**dvc.__dict__))
            embed = DvcSettings.embed(ctx, dvc, "成功設置名稱格式。", True)
        else:
            embed = DvcSettings.embed(ctx, dvc, "名稱格式不能為空。", False)
        await ctx.edit("@original", embed=embed, components=DvcSettings.components(dvc))


class DvcComponents(DvcExtension):
    """
    The extension class for the dynamic voice channel components.
    """

    async def handle_enabled(self, ctx: interactions.ComponentContext) -> Tuple[Embed, List[interactions.ActionRow]]:
        """
        Handle the enabled setting.

        :param ctx: The component context.
        :type ctx: interactions.ComponentContext

        :return: The embed and components.
        :rtype: tuple
        """
        dvc = await self.database.get_guild_dvc_settings(ctx.guild.id)
        if dvc.enabled:
            dvc.enabled = False
            await self.database.set_guild_dvc_settings(ctx.guild.id, models.DvcSettings.create(**dvc.__dict__))
            return DvcSettings.embed(ctx, dvc, "成功停用動態語音頻道。", True), DvcSettings.components(dvc)
        if not dvc.lobby or not await self.client.fetch_channel(dvc.lobby):
            return DvcSettings.embed(ctx, dvc, "請先設置大廳頻道。", False), DvcSettings.components(dvc)
        if not dvc.name:
            return DvcSettings.failed_embed(ctx, dvc, "請先設置名稱格式。", False), DvcSettings.components(dvc)
        dvc.enabled = True
        await self.database.set_guild_dvc_settings(ctx.guild.id, models.DvcSettings.create(**dvc.__dict__))
        return DvcSettings.embed(ctx, dvc, "成功啟用動態語音頻道。", True), DvcSettings.components(dvc)

    @interactions.component_callback("dvc_settings:select")
    async def dvc_settings_select(self, ctx: interactions.ComponentContext):
        """
        The component callback for the dynamic voice channel settings select menu.
        """
        option = ctx.values[0]
        current = ctx.message.embeds[0].fields[2].value.split(" ", 1)[1]
        if option == "name":
            return await ctx.send_modal(DvcSettings.name_modal(None if current == "未設置" else current[1:-1]))

        await ctx.defer(edit_origin=True)
        if option == "toggle":
            embed, components = await self.handle_enabled(ctx)
        elif option == "channel":
            embed = DvcSettings.channel_embed()
            components = DvcSettings.channel_components()
        elif option == "placeholder":
            embed, components = None, None
        elif option == "return":
            embed = Settings.features_embed()
            components = Settings.features_components(ctx)
        await ctx.edit(embed=embed, components=components)

    @interactions.component_callback("dvc_settings:channel_action_select")
    async def dvc_settings_channel_action_select(self, ctx: interactions.ComponentContext):
        """
        The component callback for the dynamic voice channel channel action select menu.
        """
        await ctx.defer(edit_origin=True)
        option = ctx.values[0]
        dvc = await self.database.get_guild_dvc_settings(ctx.guild.id)
        if option == "placeholder":
            embed, components = None, None
        elif option == "return":
            embed = DvcSettings.embed(ctx, dvc)
            components = DvcSettings.components(dvc)
        await ctx.edit(embed=embed, components=components)

    @interactions.component_callback("dvc_settings:channel_select")
    async def dvc_settings_channel_select(self, ctx: interactions.ComponentContext):
        """
        The component callback for the dynamic voice channel channel select menu.
        """
        await ctx.defer(edit_origin=True)
        dvc = await self.database.get_guild_dvc_settings(ctx.guild.id)
        dvc.lobby = ctx.values[0].id
        await self.database.set_guild_dvc_settings(ctx.guild.id, models.DvcSettings.create(**dvc.__dict__))
        embed = DvcSettings.embed(ctx, dvc, "成功設置大廳頻道。", True)
        components = DvcSettings.components(dvc)
        await ctx.edit(embed=embed, components=components)


class DvcCore(DvcExtension):
    """
    The extension class for the dynamic voice channels.
    """

    def __init__(self, client: Client):
        """
        The constructor for the extension.

        :param client: The client object.
        :type client: Client
        """
        super().__init__(client=client)
        asyncio.create_task(self.async_init())

    async def async_init(self) -> None:
        await self.database.wait_until_ready()
        async for channel_id in self.database.get_dvcs():
            if not await self.client.fetch_channel(channel_id):
                await self.database.remove_dvc(channel_id)

    async def dvc_name(self, vs: interactions.VoiceState, ori: str) -> str:
        """
        Get the name of the dynamic voice channel.

        :param vs: The voice state.
        :type vs: interactions.VoiceState
        :param ori: The original name.
        :type ori: str

        :return: The name of the dynamic voice channel.
        :rtype: str
        """
        if "{{count}}" in ori:
            ori = ori.replace("{{count}}", str(await self.database.get_dvc_count(vs.guild.id) + 1))
        return (
            ori.replace("{{id}}", str(vs.member.id))
            .replace("{{guild}}", vs.guild.name)
            .replace("{{username}}", vs.member.username)
            .replace("{{user}}", vs.member.display_name)
        )

    @interactions.listen()
    async def on_voice_state_update(self, event: VoiceStateUpdate) -> None:
        """
        The event that is triggered when a user updated their voice state.
        """
        guild_conf = await self.database.get_guild_dvc_settings((event.after or event.before).guild.id)
        if not guild_conf.enabled:
            return

        if event.after and event.after.channel.id == guild_conf.lobby:
            channel = await event.after.channel.guild.create_voice_channel(
                name=await self.dvc_name(event.after, guild_conf.name),
                category=event.after.channel.category,
                position=event.after.channel.position + 1,
                reason="動態語音頻道創建",
            )
            try:
                await event.after.member.move(channel.id)
            except Exception:  # pylint: disable=broad-except
                await channel.delete("無法移動成員到動態語音頻道")
            else:
                await self.database.add_dvc(channel.id, event.after.member.id, event.after.guild.id)
                ...  # TODO: control panel in voice channel

        if (
            # the user left the channel or moved to another channel
            event.before
            and (not event.after or event.after.channel.id != event.before.channel.id)
            # the channel is empty
            and len(event.before.channel.members) >= 1
            # the channel is a dynamic voice channel
            and await self.database.is_dvc(event.before.channel.id)
        ):
            await self.database.remove_dvc(event.before.channel.id)
            await event.before.channel.delete("動態語音頻道移除")


def setup(client: Client):
    """
    The setup function for the extension.

    :param client: The client object.
    :type client: Client
    """
    DvcCore(client)
    DvcComponents(client)
    DvcModals(client)
