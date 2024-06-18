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
        name: Optional[str] = None,
        description: Optional[str] = None,
        url: Optional[str] = None,
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
        self.set_author(
            name=f"猫戸助手 - {name}" if name else "猫戸助手", url=url, icon_url=self._client.user.avatar.url
        )

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
        return cls("操作失敗", f"你不能使用這個{'按鈕' if ctype == 'button' else '選單'}。", success=False)

    @classmethod
    def traceback(cls, error: Exception) -> "Embed":
        """
        Returns an embed with a traceback response.

        :param client: The client instance.
        :type client: Client
        :param error: The error that occurred.
        :type error: Exception
        """
        return cls("錯誤", f"執行操作時發生了一個錯誤：```{error}```", success=False)
