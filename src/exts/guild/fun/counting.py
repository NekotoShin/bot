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

import ast
import math
import operator as op
from typing import List, Tuple

import interactions
from interactions.api.events import MessageCreate

from src.main import BaseExtension, Client
from src.utils import CountingSettings, Embed, GuildFunSettings


class Counting(BaseExtension):
    """
    The extension class for the counting game.
    """

    operators = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.Mult: op.mul,
        ast.Div: op.truediv,
        ast.Pow: op.pow,
        ast.BitXor: op.xor,
        ast.USub: op.neg,
        ast.Mod: op.mod,
        ast.FloorDiv: op.floordiv,
    }

    def eval_expr(self, expr):
        return self._eval_expr(ast.parse(expr, mode="eval").body)

    def _eval_expr(self, node):
        if isinstance(node, ast.Constant):
            return node.n
        elif isinstance(node, ast.BinOp):
            return self.operators[type(node.op)](self._eval_expr(node.left), self._eval_expr(node.right))
        elif isinstance(node, ast.UnaryOp):
            return self.operators[type(node.op)](self._eval_expr(node.operand))
        else:
            raise TypeError(node)

    @interactions.listen()
    async def on_message_create(self, event: MessageCreate):
        if not event.message.content or (event.message.author and event.message.author.bot) or not event.message.guild:
            return
        counting = await self.database.get_guild_counting(event.message.guild.id)
        if not counting.enabled or counting.channel != event.message.channel.id:
            return
        if any(i not in "0123456789+-*/^.÷x%" for i in event.message.content):
            return
        content = event.message.content.replace("÷", "/").replace("x", "*")
        try:
            value = math.trunc(self.eval_expr(content))
        except (TypeError, ZeroDivisionError):
            return
        if counting.current != 0 and counting.previous == event.message.author.id:
            await event.message.add_reaction("❌")
            await event.message.reply(embed=Embed("你不能連續數兩次！", success=False))
            await self.database.reset_current_count(event.message.guild.id, counting.current)
        elif round(value) != counting.current + 1:
            await event.message.add_reaction("❌")
            if counting.current == 0:
                await event.message.reply(embed=Embed("你需要從`1`開始數！", success=False))
            else:
                await event.message.reply(
                    embed=Embed(f"下個數字是`{counting.current + 1}`才對！\n請從`1`重新開始！", success=False)
                )
                await self.database.reset_current_count(event.message.guild.id, counting.current)
        else:
            if (counting.current + 1) == 100:
                emoji = "💯"
            elif (counting.current + 1) % 100 == 0:
                emoji = "🎉"
            else:
                emoji = "✅"
            await event.message.add_reaction(emoji)
            await self.database.inc_current_count(event.message.guild.id, event.message.author.id)

    async def handle_enabled(self, ctx: interactions.ComponentContext) -> Tuple[Embed, List[interactions.ActionRow]]:
        """
        Handle the enabled setting.

        :param ctx: The component context.
        :type ctx: interactions.ComponentContext

        :return: The embed and components.
        :rtype: tuple
        """
        counting = await self.database.get_guild_counting(ctx.guild.id)
        if counting.enabled:
            counting.enabled = False
            counting.previous = -1
            counting.current = 0
            await self.database.set_guild_counting(ctx.guild.id, counting)
            return CountingSettings.embed(ctx, counting, "成功停用數數字遊戲。", True), CountingSettings.components(
                counting
            )
        if counting.channel == -1 or not (c := await self.client.fetch_channel(counting.channel)):
            return CountingSettings.embed(ctx, counting, "請先設置遊戲頻道。", False), CountingSettings.components(
                counting
            )
        counting.enabled = True
        await self.database.set_guild_counting(ctx.guild.id, counting)
        await c.send(embed=Embed("數數字遊戲開始！\n請從`1`開始數數字～", success=True))
        return CountingSettings.embed(ctx, counting, "成功啟用數數字遊戲。", True), CountingSettings.components(
            counting
        )

    @interactions.component_callback("counting_settings:select")
    async def counting_settings_select(self, ctx: interactions.ComponentContext):
        """
        The component callback for the counting settings select menu.
        """
        await ctx.defer(edit_origin=True)
        option = ctx.values[0]
        if option == "toggle":
            embed, components = await self.handle_enabled(ctx)
        elif option == "channel":
            counting = await self.database.get_guild_counting(ctx.guild.id)
            if counting.enabled and counting.channel != -1 and ctx.guild.get_channel(counting.channel) is not None:
                embed = CountingSettings.embed(ctx, counting, "請先停用數數字遊戲。", False)
                components = CountingSettings.components(counting)
            else:
                embed = CountingSettings.channel_embed()
                components = CountingSettings.channel_components()
        elif option == "placeholder":
            embed, components = None, None
        elif option == "return":
            embed = GuildFunSettings.embed()
            components = GuildFunSettings.components(ctx)
        await ctx.edit(embed=embed, components=components)

    @interactions.component_callback("counting_settings:channel_action_select")
    async def counting_settings_channel_action_select(self, ctx: interactions.ComponentContext):
        """
        The component callback for the counting channel action select menu.
        """
        await ctx.defer(edit_origin=True)
        option = ctx.values[0]
        counting = await self.database.get_guild_counting(ctx.guild.id)
        if option == "placeholder":
            embed, components = None, None
        elif option == "return":
            embed = CountingSettings.embed(ctx, counting)
            components = CountingSettings.components(counting)
        await ctx.edit(embed=embed, components=components)

    @interactions.component_callback("counting_settings:channel_select")
    async def counting_settings_channel_select(self, ctx: interactions.ComponentContext):
        """
        The component callback for the counting channel select menu.
        """
        await ctx.defer(edit_origin=True)
        counting = await self.database.get_guild_counting(ctx.guild.id)
        if counting.enabled and counting.channel != -1 and ctx.guild.get_channel(counting.channel) is not None:
            embed = CountingSettings.embed(ctx, counting, "請先停用數數字遊戲。", False)
        else:
            counting.channel = ctx.values[0].id
            counting.enabled = False
            await self.database.set_guild_counting(ctx.guild.id, counting)
            embed = CountingSettings.embed(ctx, counting, "成功設置遊戲頻道。", True)
        components = CountingSettings.components(counting)
        await ctx.edit(embed=embed, components=components)


def setup(client: Client):
    """
    The setup function for the extension.

    :param client: The client object.
    :type client: Client
    """
    Counting(client)
