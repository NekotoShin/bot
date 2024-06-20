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

from typing import Any, Protocol, TypeVar

import interactions
from interactions.api.http.route import Route
from interactions.models.internal.protocols import CanRequest as CanRequestBase

__all__ = ("CanRequest", "CanExecute")

T_co = TypeVar("T_co", covariant=True)


class CanRequest(CanRequestBase):
    """
    The modified CanRequest class.
    """

    async def request(
        self,
        route: Route,
        payload: list | dict | None = None,
        files: list[interactions.UPLOADABLE_TYPE] | None = None,
        reason: str | None = None,
        params: dict | None = None,
        skip_ratelimit: bool = False,
        **kwargs: dict,
    ) -> str | dict[str, Any] | None:
        raise NotImplementedError("Derived classes need to implement this.")


class CanExecute(Protocol[T_co]):
    async def execute(self, *args, **kwargs):
        raise NotImplementedError("Derived classes need to implement this.")
