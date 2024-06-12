"""
The configuration module for the bot.
"""

from typing import Any, Dict, Optional, TypeVar

import tomli

__all__ = ("Config",)

T = TypeVar("T")


class Config:
    """
    The configuration class of the bot.
    """

    def __init__(self, path: str) -> None:
        self._path = path
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load the configuration file.
        This is an internal method and should not be called directly.

        :raises TOMLDecodeError: Raised when the config is invalid.
        :raises FileNotFoundError: Raised when the file is not found.

        :return: The configuration file.
        :rtype: Dict[str, Any]
        """
        with open(self._path, "rb") as f:
            return tomli.load(f)

    def get(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """
        Get a key from the configuration file.

        :param key: The key to get.
        :type key: str
        :param default: The default value if the key is not found.
        :type default: Optional[T]

        :return: The value of the key.
        :rtype: Optional[T]
        """
        return self._config.get(key, default)

    def reload(self) -> None:
        """
        Reload the configuration file.
        """
        self._config = self._load_config()

    @property
    def config(self) -> Dict[str, Any]:
        """
        Get the configuration as a dictionary.

        :return: The configurations.
        :rtype: Dict[str, Any]
        """
        return self._config

    def __getitem__(self, key: str) -> Any:
        """
        Get a key from the configuration file.

        :param key: The key to get.
        :type key: str

        :return: The value of the key.
        :rtype: Any
        """
        return self._config[key]
