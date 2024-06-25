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
import re
from typing import List, Tuple

import interactions  # noqa: F401
from interactions import MISSING, TYPE_ALL_CHANNEL, Absent
from interactions.api.events import ChannelDelete, VoiceStateUpdate

from src.main import BaseExtension, Client
from src.utils import DvcPanel, DvcSettings, Embed, GuildGeneralSettings, Ratelimited


class DvcModals(BaseExtension):
    """
    The extension class for the dynamic voice channel modals.
    """

    async def edit_channel(
        self,
        channel: "TYPE_ALL_CHANNEL",
        *,
        name: Absent[str] = MISSING,
        bitrate: Absent[int] = MISSING,
        user_limit: Absent[int] = MISSING,
        reason: Absent[str] = MISSING,
        **kwargs,
    ) -> "TYPE_ALL_CHANNEL":
        """
        Edits the channel but raises an exception on 429.
        """
        payload = {
            "name": name,
            "bitrate": bitrate,
            "user_limit": user_limit,
            **kwargs,
        }
        channel_data = await self.client.http.modify_channel_raise(channel.id, payload, reason)
        if not channel_data:
            raise Ratelimited(
                "You have changed this channel too frequently, you need to wait a while before trying again."
            ) from None

        return self.client.cache.place_channel_data(channel_data)

    @interactions.modal_callback("dvc_settings:name")
    async def name_modal(self, ctx: interactions.ModalContext, name: str, **_):
        """
        The modal callback for the dynamic voice channel name modal.
        """
        await ctx.defer(edit_origin=True)
        dvc = await self.database.get_guild_dvc_settings(ctx.guild.id)
        if name := name.strip():
            dvc.name = name
            await self.database.set_guild_dvc_settings(ctx.guild.id, dvc)
            embed = DvcSettings.embed(ctx, dvc, "成功設置名稱格式。", True)
        else:
            embed = DvcSettings.embed(ctx, dvc, "名稱格式不能為空。", False)
        await ctx.edit("@original", embed=embed, components=DvcSettings.components(dvc))

    @interactions.modal_callback("dvc_panel:name")
    async def dvc_panel_name(self, ctx: interactions.ModalContext, name: str):
        """
        The component callback for the dynamic voice channel name modal.
        """
        await ctx.defer(ephemeral=True)
        owner = await self.database.get_dvc_owner(ctx.channel.id)
        if ctx.author.id != owner:
            return await ctx.send(embed=Embed("只有頻道擁有者才能修改此設定。", False))
        if not name.strip():
            return await ctx.send(embed=Embed("名稱不能為空。", False))
        try:
            await self.edit_channel(ctx.channel, name=name, reason="動態語音頻道 - 修改名稱")
        except Ratelimited:
            return await ctx.send(embed=Embed("頻道設定變更過於頻繁，請稍後再試。", False))
        await ctx.send(embed=Embed("成功修改語音頻道名稱。", True))

    @interactions.modal_callback("dvc_panel:bitrate")
    async def dvc_panel_bitrate(self, ctx: interactions.ModalContext, bitrate: str):
        """
        The component callback for the dynamic voice channel bitrate select menu.
        """
        await ctx.defer(ephemeral=True)
        owner = await self.database.get_dvc_owner(ctx.channel.id)
        if ctx.author.id != owner:
            return await ctx.send(embed=Embed("只有頻道擁有者才能修改此設定。", False))
        max_bitrate = [96, 128, 256, 384][ctx.guild.premium_tier or 0]
        try:
            bitrate = int(bitrate)
        except ValueError:
            return await ctx.send(embed=Embed(f"請輸入有效的數字 (8-{max_bitrate})。", False))
        if not 8 <= bitrate <= max_bitrate:
            return await ctx.send(embed=Embed(f"位元率必須在 8-{max_bitrate}kbps 之間。", False))
        try:
            await self.edit_channel(ctx.channel, bitrate=bitrate * 1000, reason="動態語音頻道 - 修改位元率")
        except Ratelimited:
            return await ctx.send(embed=Embed("頻道設定變更過於頻繁，請稍後再試。", False))
        await ctx.send(embed=Embed("成功修改語音頻道位元率。", True))

    @interactions.modal_callback("dvc_panel:limit")
    async def dvc_panel_limit(self, ctx: interactions.ModalContext, limit: str):
        """
        The component callback for the dynamic voice channel limit select menu.
        """
        await ctx.defer(ephemeral=True)
        owner = await self.database.get_dvc_owner(ctx.channel.id)
        if ctx.author.id != owner:
            return await ctx.send(embed=Embed("只有頻道擁有者才能修改此設定。", False))
        try:
            limit = int(limit)
        except ValueError:
            return await ctx.send(embed=Embed("請輸入有效的數字。", False))
        if not 0 <= limit <= 99:
            return await ctx.send(embed=Embed("人數限制必須在 0-99 之間。", False))
        try:
            await self.edit_channel(ctx.channel, user_limit=limit, reason="動態語音頻道 - 修改人數限制")
        except Ratelimited:
            return await ctx.send(embed=Embed("頻道設定變更過於頻繁，請稍後再試。", False))
        await ctx.send(embed=Embed("成功修改語音頻道人數限制。", True))


class DvcComponents(BaseExtension):
    """
    The extension class for the dynamic voice channel components.
    """

    transfer_regex = re.compile(r"dvc_panel:transfer_select:(\d+)")

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
            await self.database.set_guild_dvc_settings(ctx.guild.id, dvc)
            async for i in self.database.get_guild_dvcs(ctx.guild.id):
                await self.client.http.delete_channel(i)
            return DvcSettings.embed(ctx, dvc, "成功停用動態語音頻道。", True), DvcSettings.components(dvc)
        if dvc.lobby == -1 or not await self.client.fetch_channel(dvc.lobby):
            return DvcSettings.embed(ctx, dvc, "請先設置大廳頻道。", False), DvcSettings.components(dvc)
        if not dvc.name:
            return DvcSettings.embed(ctx, dvc, "請先設置名稱格式。", False), DvcSettings.components(dvc)
        dvc.enabled = True
        await self.database.set_guild_dvc_settings(ctx.guild.id, dvc)
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
            embed = GuildGeneralSettings.embed()
            components = GuildGeneralSettings.components(ctx)
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
        await self.database.set_guild_dvc_settings(ctx.guild.id, dvc)
        embed = DvcSettings.embed(ctx, dvc, "成功設置大廳頻道。", True)
        components = DvcSettings.components(dvc)
        await ctx.edit(embed=embed, components=components)

    @interactions.component_callback("dvc_panel:select")
    async def dvc_panel_select(self, ctx: interactions.ModalContext):
        """
        The component callback for the dynamic voice channel panel select menu.
        """
        option = ctx.values[0]
        if option == "placeholder":
            await ctx.defer(edit_origin=True)
            owner = await self.database.get_dvc_owner(ctx.channel.id)
            return await ctx.edit_origin(embed=DvcPanel.embed(owner, ctx.channel.id), components=DvcPanel.components())

        if option in ["name", "bitrate", "limit"]:
            owner = await self.database.get_dvc_owner(ctx.channel.id)
            if ctx.author.id != owner:
                await ctx.defer(ephemeral=True)
                await ctx.send(embed=Embed("只有頻道擁有者才能修改此設定。", False))
            else:
                if option == "bitrate":
                    modal = DvcPanel.bitrate_modal(ctx.channel.bitrate, ctx.guild.premium_tier or 0)
                elif option == "limit":
                    modal = DvcPanel.limit_modal(ctx.channel.user_limit)
                else:
                    modal = DvcPanel.name_modal(ctx.channel.name)
                await ctx.send_modal(modal)
            return await ctx.message.edit(
                embed=DvcPanel.embed(owner, ctx.channel.id), components=DvcPanel.components()
            )

        await ctx.defer(ephemeral=True)
        owner = await self.database.get_dvc_owner(ctx.channel.id)
        if ctx.author.id != owner:
            await ctx.send(embed=Embed("只有頻道擁有者才能修改此設定。", False))
        elif option == "transfer":
            await ctx.send(embed=DvcPanel.transfer_embed(), components=DvcPanel.transfer_components(ctx.message.id))
            await ctx.message.edit(embed=DvcPanel.embed(owner, ctx.channel.id), components=DvcPanel.components())
        elif option == "close":
            await ctx.send(embed=Embed("正在關閉動態語音頻道...", True))
            await ctx.channel.delete("動態語音頻道關閉")

    @interactions.component_callback(transfer_regex)
    async def dvc_panel_transfer_select(self, ctx: interactions.ComponentContext):
        """
        The component callback for the dynamic voice channel transfer select menu.
        """
        await ctx.defer(edit_origin=True)
        member: interactions.Member = ctx.values[0]
        owner = await self.database.get_dvc_owner(ctx.channel.id)
        if ctx.author.id != owner:
            return await ctx.edit_origin(embed=Embed("只有頻道擁有者才能修改此設定。", False), components=[])
        if member.id == owner:
            return await ctx.edit_origin(embed=Embed("你已經是頻道擁有者。", False))
        if member.bot:
            return await ctx.edit_origin(embed=Embed("機器人不能成為頻道擁有者。", False))
        if not member.voice or member.voice.channel.id != ctx.channel.id:
            return await ctx.edit_origin(embed=Embed("該成員不在此頻道。", False))
        await self.database.set_dvc_owner(ctx.channel.id, member.id)
        await ctx.edit_origin(embed=Embed("成功轉移頻道擁有權。", True), components=[])
        msg = await ctx.channel.fetch_message(self.transfer_regex.match(ctx.custom_id).group(1))
        await msg.edit(embed=DvcPanel.embed(member.id, ctx.channel.id), components=DvcPanel.components())


class DvcCore(BaseExtension):
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
            ori = ori.replace("{{count}}", str(await self.database.get_guild_dvc_count(vs.guild.id) + 1))
        return ori.replace("{{username}}", vs.member.username).replace("{{user}}", vs.member.display_name)

    @interactions.listen()
    async def on_voice_state_update(self, event: VoiceStateUpdate) -> None:
        """
        The event that is triggered when a user updated their voice state.
        """
        guild_conf = await self.database.get_guild_dvc_settings((event.after or event.before).guild.id)
        if not guild_conf.enabled:
            return

        # handle channel creation
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
                await channel.send(
                    embed=DvcPanel.embed(event.after.member.id, channel.id), components=DvcPanel.components()
                )
                msg = await channel.send(event.after.member.mention)
                await msg.delete()

        # handle channel deletion
        if (
            # the user left the channel or moved to another channel
            event.before
            and (not event.after or event.after.channel.id != event.before.channel.id)
            # the channel still exists and not nuked away
            and event.before.channel
            # the channel is empty
            and len(event.before.channel.voice_members) <= 1
            # the channel is a dynamic voice channel
            and await self.database.is_dvc(event.before.channel.id)
        ):
            await event.before.channel.delete("動態語音頻道移除")

    @interactions.listen()
    async def on_channel_delete(self, event: ChannelDelete) -> None:
        """
        The event that is triggered when a channel is deleted.
        """
        if event.channel.type == interactions.ChannelType.GUILD_VOICE:
            await self.database.remove_dvc(event.channel.id)


def setup(client: Client):
    """
    The setup function for the extension.

    :param client: The client object.
    :type client: Client
    """
    DvcCore(client)
    DvcComponents(client)
    DvcModals(client)
