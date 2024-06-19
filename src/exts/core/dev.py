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

import glob
import re
from functools import lru_cache
from typing import List, Literal, Optional, Tuple

import interactions
from interactions.ext import prefixed_commands

from src.main import BaseExtension, Client
from src.utils import Embed


class DeveloperModal(BaseExtension):
    """
    The extension class for the developer modal.
    """

    eval_regex = re.compile(r"(\d+):developer:eval")
    extensions_regex = re.compile(r"(\d+):developer:extensions:(\d+):(load|unload|reload)")

    ext_modes = {"load": "啟用", "unload": "停用", "reload": "重新載入"}

    @staticmethod
    def eval_modal(author_id: int) -> interactions.Modal:
        """
        The modal for the eval command.
        """
        return interactions.Modal(
            interactions.InputText(
                label="Python程式碼",
                style=interactions.TextStyles.PARAGRAPH,
                custom_id="code",
                placeholder="請輸入需要執行的Python程式碼",
            ),
            title="執行程式碼",
            custom_id=f"{author_id}:developer:eval",
        )

    @interactions.modal_callback(eval_regex)
    async def eval_callback(self, ctx: interactions.ModalContext, code: str):
        try:
            result = eval(code)  # pylint: disable=eval-used
        except Exception as e:  # pylint: disable=broad-except
            desc = f"執行操作時發生了一個錯誤：```{e}```"
            success = False
        else:
            desc = f"`{result}`"
            success = True
        matched = self.eval_regex.match(ctx.custom_id)
        await ctx.edit(
            "@original",
            embed=Embed(desc, success),
            components=DeveloperComponents.eval_completed(matched.group(1)),
        )

    @staticmethod
    def extensions(author_id: int, ori: int, option: Literal["load", "unload", "reload"]) -> interactions.Modal:
        """
        The modal for the extensions command.
        """
        return interactions.Modal(
            interactions.InputText(
                label="插件名稱",
                style=interactions.TextStyles.SHORT,
                custom_id="extension",
                placeholder="請輸入要執行的插件名稱",
            ),
            title=f"{DeveloperModal.ext_modes[option]}插件",
            custom_id=f"{author_id}:developer:extensions:{ori}:{option}",
        )

    @interactions.modal_callback(extensions_regex)
    async def extensions_callback(self, ctx: interactions.ModalContext, extension: str):
        regex = self.extensions_regex.match(ctx.custom_id)
        author_id, ori, option = regex.group(1), regex.group(2), regex.group(3)

        loaded, unloaded = DeveloperCore.get_extensions(self.client)
        reload_self = False
        success = False
        if not extension.startswith("src.exts."):
            extension = f"src.exts.{extension}"
        if option == "load":
            if extension in loaded:
                desc = f"插件 `{extension}` 已經在啟用狀態。"
            elif extension not in unloaded:
                desc = f"插件 `{extension}` 不存在。"
            else:
                self.client.load_extension(extension)
                desc = f"插件 `{extension}` 已經成功啟用。"
                success = True
        elif option == "unload":
            if extension in unloaded:
                desc = f"插件 `{extension}` 已經在停用狀態。"
            elif extension not in loaded:
                desc = f"插件 `{extension}` 不存在。"
            elif extension == self.extension_name:
                desc = "無法停用開發者插件。"
            else:
                self.client.unload_extension(extension)
                desc = f"插件 `{extension}` 已經成功停用。"
                success = True
        elif option == "reload":
            if extension in unloaded:
                desc = f"插件 `{extension}` 處於在停用狀態。"
            elif extension not in loaded:
                desc = f"插件 `{extension}` 不存在。"
            elif extension == self.extension_name:
                desc = "即將重新載入開發者插件。"
                success = True
                reload_self = True
            else:
                self.client.reload_extension(extension)
                desc = f"插件 `{extension}` 已經成功重新載入。"
                success = True
        embed = Embed(desc, success)
        await ctx.edit(ori, embed=embed, components=DeveloperComponents.extensions(author_id))
        if reload_self:
            self.client.reload_extension(self.extension_name)


class DeveloperComponents(BaseExtension):
    """
    The extension class for the developer components.
    """

    developer_regex = re.compile(r"(\d+):developer:select")
    eval_completed_regex = re.compile(r"(\d+):developer:eval:completed")
    extensions_regex = re.compile(r"(\d+):developer:extensions")

    @staticmethod
    def developer(author_id: int) -> List[interactions.ActionRow]:
        """
        The components for the prefixed developer command.
        """
        return [
            interactions.ActionRow(
                interactions.StringSelectMenu(
                    interactions.StringSelectOption(
                        label="NekoOS • 開發者工具",
                        value="placeholder",
                        emoji=interactions.PartialEmoji(name="🛠️"),
                        default=True,
                    ),
                    interactions.StringSelectOption(
                        label="插件管理",
                        description="管理機器人的插件 (啟用/停用/重新載入)",
                        value="extensions",
                        emoji=interactions.PartialEmoji(name="🔌"),
                    ),
                    interactions.StringSelectOption(
                        label="執行程式碼",
                        description="透過機器人執行Python程式碼 (eval)",
                        value="eval",
                        emoji=interactions.PartialEmoji(name="💻"),
                    ),
                    interactions.StringSelectOption(
                        label="關閉機器人",
                        description="中斷機器人與Discord和資料庫的連接並停止伺服器",
                        value="shutdown",
                        emoji=interactions.PartialEmoji(name="🛑"),
                    ),
                    custom_id=f"{author_id}:developer:select",
                )
            )
        ]

    @staticmethod
    def shutdown() -> List[interactions.ActionRow]:
        """
        The components for the shutdown command.
        """
        return [
            interactions.ActionRow(
                interactions.StringSelectMenu(
                    interactions.StringSelectOption(
                        label="NekoOS • 關閉機器人",
                        value="placeholder",
                        emoji=interactions.PartialEmoji(name="🛑"),
                        default=True,
                    ),
                    disabled=True,
                )
            )
        ]

    @interactions.component_callback(developer_regex)
    async def developer_select_callback(self, ctx: interactions.ComponentContext):
        author_id = int(self.developer_regex.match(ctx.custom_id).group(1))
        if ctx.author.id != author_id:
            return await ctx.respond(embed=Embed.declined("select"), ephemeral=True)
        option = ctx.values[0]
        if option == "eval":
            return await ctx.send_modal(DeveloperModal.eval_modal(author_id))

        await ctx.defer(edit_origin=True)
        if option == "extensions":
            await ctx.edit_origin(
                embed=Embed("管理機器人插件的各項功能"),
                components=DeveloperComponents.extensions(author_id),
            )
        elif option == "shutdown":
            await ctx.edit_origin(
                embed=Embed("即將關閉機器人。", success=True),
                components=DeveloperComponents.shutdown(),
            )
            await self.client.stop()

    @staticmethod
    def eval_completed(author_id: int) -> List[interactions.ActionRow]:
        """
        The components for the eval command after completion.
        """
        return [
            interactions.ActionRow(
                interactions.StringSelectMenu(
                    interactions.StringSelectOption(
                        label="NekoOS • 執行程式碼",
                        value="placeholder",
                        emoji=interactions.PartialEmoji(name="💻"),
                        default=True,
                    ),
                    interactions.StringSelectOption(
                        label="再次執行",
                        description="繼續執行其他Python程式碼",
                        value="eval",
                        emoji=interactions.PartialEmoji(name="🔁"),
                    ),
                    interactions.StringSelectOption(
                        label="返回",
                        description="回到全部開發者工具",
                        value="back",
                        emoji=interactions.PartialEmoji(name="🔙"),
                    ),
                    custom_id=f"{author_id}:developer:eval:completed",
                )
            )
        ]

    @interactions.component_callback(eval_completed_regex)
    async def eval_completed_callback(self, ctx: interactions.ComponentContext):
        author_id = int(self.eval_completed_regex.match(ctx.custom_id).group(1))
        if ctx.author.id != author_id:
            return await ctx.respond(embed=Embed.declined("select"), ephemeral=True)
        option = ctx.values[0]
        if option == "eval":
            return await ctx.send_modal(DeveloperModal.eval_modal(author_id))
        await ctx.defer(edit_origin=True)
        if option == "back":
            return await ctx.edit(
                embed=DeveloperCore.developer_embed(), components=DeveloperComponents.developer(author_id)
            )

    @staticmethod
    def extensions(author_id: int, skip_list: Optional[bool] = False) -> List[interactions.ActionRow]:
        """
        The components for the extensions command.
        """
        options = [
            interactions.StringSelectOption(
                label="NekoOS • 插件管理",
                value="placeholder",
                emoji=interactions.PartialEmoji(name="🔌"),
                default=True,
            ),
        ]

        if not skip_list:
            options.append(
                interactions.StringSelectOption(
                    label="列表",
                    description="列出所有已經啟用及可用的插件",
                    value="list",
                    emoji=interactions.PartialEmoji(name="📋"),
                )
            )
        options.extend(
            [
                interactions.StringSelectOption(
                    label="啟用",
                    description="啟用指定的插件",
                    value="load",
                    emoji=interactions.PartialEmoji(name="🟢"),
                ),
                interactions.StringSelectOption(
                    label="停用",
                    description="停用指定的插件",
                    value="unload",
                    emoji=interactions.PartialEmoji(name="🔴"),
                ),
                interactions.StringSelectOption(
                    label="重新載入",
                    description="重新載入指定的插件",
                    value="reload",
                    emoji=interactions.PartialEmoji(name="🔄"),
                ),
                interactions.StringSelectOption(
                    label="返回",
                    description="回到全部開發者工具",
                    value="back",
                    emoji=interactions.PartialEmoji(name="🔙"),
                ),
            ]
        )
        return [
            interactions.ActionRow(
                interactions.StringSelectMenu(
                    *options,
                    custom_id=f"{author_id}:developer:extensions",
                )
            )
        ]

    @interactions.component_callback(extensions_regex)
    async def extensions_callback(self, ctx: interactions.ComponentContext):
        author_id = int(self.extensions_regex.match(ctx.custom_id).group(1))
        if ctx.author.id != author_id:
            return await ctx.respond(embed=Embed.declined("select"), ephemeral=True)
        option = ctx.values[0]
        if option in ("load", "unload", "reload"):
            return await ctx.send_modal(DeveloperModal.extensions(author_id, ctx.message.id, option))

        await ctx.defer(edit_origin=True)
        if option == "list":
            loaded, unloaded = DeveloperCore.get_extensions(self.client)
            embed = Embed("所有已經啟用及可用的插件")
            if not loaded:
                value = "\\*沒有啟用的插件\\*"
            else:
                value = "\n".join(i.removeprefix("src.exts.") for i in loaded)
                value = f"```\n{value}\n```"
            embed.add_field(name="已啟用的插件", value=value)
            if not unloaded:
                value = "\\*沒有可用的插件\\*"
            else:
                value = "\n".join(i.removeprefix("src.exts.") for i in unloaded)
                value = f"```\n{value}\n```"
            embed.add_field(name="可用的插件", value=value)
            await ctx.edit(embed=embed, components=DeveloperComponents.extensions(author_id, True))
        elif option == "back":
            await ctx.edit(embed=DeveloperCore.developer_embed(), components=DeveloperComponents.developer(author_id))


class DeveloperCore(BaseExtension):
    """
    The extension class for the development.
    """

    def __init__(self, client: Client):
        super().__init__(client)
        self.add_extension_prerun(self.pre_run)
        self.set_extension_error(self.error_handler)

    @staticmethod
    @lru_cache(maxsize=1)
    def get_extensions(client: Client) -> Tuple[List[str], List[str]]:
        """
        Get the loaded and unloaded extensions.
        """
        all_exts = [
            i.removesuffix(".py").replace("/", ".")
            for i in glob.glob("src/exts/**/*.py", recursive=True)
            if not i.endswith("template.py") and not i.endswith("__init__.py")
        ]
        loaded = {i.extension_name for i in client.ext.values()}
        return loaded, [i for i in all_exts if i not in loaded]

    @staticmethod
    def developer_embed() -> Embed:
        """
        The embed for the developer command.
        """
        return Embed("僅限機器人開發者使用的功能")

    @prefixed_commands.prefixed_command(name="developer", aliases=["dev", "owner", "help"])
    @interactions.check(interactions.is_owner())
    async def developer(self, ctx: prefixed_commands.PrefixedContext):
        await ctx.reply(embed=DeveloperCore.developer_embed(), components=DeveloperComponents.developer(ctx.author.id))

    async def pre_run(self, ctx: prefixed_commands.PrefixedContext):
        self.logger.warning(
            f"Developer command !{ctx.command.qualified_name} executed by " f"{ctx.author} ({ctx.author.id})."
        )

    async def error_handler(self, error: Exception, context: interactions.BaseContext):
        if isinstance(error, interactions.errors.CommandCheckFailure):
            return
        return self.client.dispatch(interactions.events.CommandError(ctx=context, error=error))

    def drop(self) -> None:
        """
        Teardown the extension.

        This will remove all prefixed commands before unloading.
        * Default behavior only removes the commands after unloading,
        * which will make the commands "duplicated" when reloading.
        """
        for name in self.client.prefixed._ext_command_list[  # pylint: disable=protected-access
            self.extension_name
        ].copy():
            self.client.prefixed.remove_command(name)
        super().drop()


def setup(client: Client):
    """
    The setup function for the extension.

    :param client: The client object.
    :type client: Client
    """
    DeveloperComponents(client)
    DeveloperModal(client)
    DeveloperCore(client)
