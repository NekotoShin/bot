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

from typing import TYPE_CHECKING, Literal, Optional

import interactions

if TYPE_CHECKING:
    from src.main import Client

__all__ = ("Embed",)


class Embed(interactions.Embed):
    """
    This class contains methods to generate embed responses.
    """

    _client: "Client" = None

    @classmethod
    def set_client(cls, client: "Client") -> None:
        """
        Sets the client instance.

        :param client: The client instance.
        :type client: Client
        """
        cls._client = client

    def __init__(
        self,
        description: Optional[str] = None,
        success: Optional[bool] = None,
        **kwargs,
    ) -> None:
        if "color" in kwargs and success is not None:
            raise ValueError("You cannot specify the color and success parameters at the same time.")
        if success is not None:
            kwargs["color"] = "#57F287" if success else "#ED4245"
        else:
            kwargs["color"] = kwargs.get("color", "#FEE75C")
        if description:
            description = f"<:reply:1252488534619852821> {description}"
            kwargs["description"] = description.replace(self._client.http.token, "[REDACTED TOKEN]")

        super().__init__(**kwargs)
        self.set_author(name="猫戸助手", icon_url=self._client.user.avatar.url)

    @classmethod
    def declined(cls, ctype: Optional[Literal["button", "select"]] = "button") -> "Embed":
        """
        Returns an embed with a declined response.

        :param client: The client instance.
        :type client: Client
        :param ctype: The type of the component, defaults to "button"
        :type ctype: Optional[Literal["button", "select"]]
        """
        if ctype not in ("button", "select"):
            raise ValueError("The component type must be either 'button' or 'select'.")
        return cls(f"你不能使用這個{'按鈕' if ctype == 'button' else '選單'}。", success=False)
