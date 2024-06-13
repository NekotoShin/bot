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
