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
from typing import TYPE_CHECKING, Any, cast
from urllib.parse import quote as _uriquote

import discord_typings
import interactions
from aiohttp import FormData
from interactions.api.http.http_client import HTTPClient
from interactions.api.http.route import Route
from interactions.client.utils import dict_filter, response_decode

from src.utils import Ratelimited

from .protocols import CanRequest

if TYPE_CHECKING:
    from interactions.models.discord.snowflake import Snowflake_Type

__all__ = ("ModifiedHTTPClient",)


class RaiseRequests(CanRequest):
    """
    The modified requests class that raise an exception on 429 instead of waiting out and retrying.
    """

    async def modify_channel_raise(
        self, channel_id: "Snowflake_Type", data: dict, reason: str | None = None
    ) -> discord_typings.ChannelData:
        """
        Update a channel's settings, returns the updated channel object on success.

        Args:
            channel_id: The ID of the channel to update
            data: The data to update with
            reason: An optional reason for the audit log

        Returns:
            Channel object on success

        """
        result = await self.request(
            Route("PATCH", "/channels/{channel_id}", channel_id=channel_id),
            payload=data,
            reason=reason,
            skip_ratelimit=True,
        )
        return cast(discord_typings.ChannelData, result)


class ModifiedHTTPClient(HTTPClient, RaiseRequests):
    """
    The modified HTTP client.
    """

    async def request(  # noqa: C901
        self,
        route: Route,
        payload: list | dict | None = None,
        files: list[interactions.UPLOADABLE_TYPE] | None = None,
        reason: str | None = None,
        params: dict | None = None,
        skip_ratelimit: bool = False,
        **kwargs: dict,
    ) -> str | dict[str, Any] | None:
        """
        Make a request to discord.
        """
        if not skip_ratelimit:
            return await super().request(route, payload, files, reason, params, **kwargs)

        kwargs["headers"] = {"User-Agent": self.user_agent}
        if self.token:
            kwargs["headers"]["Authorization"] = f"Bot {self.token}"
        if reason:
            kwargs["headers"]["X-Audit-Log-Reason"] = _uriquote(reason, safe="/ ")

        if isinstance(payload, (list, dict)) and not files:
            kwargs["headers"]["Content-Type"] = "application/json"
        if isinstance(params, dict):
            kwargs["params"] = dict_filter(params)

        for attempt in range(self._max_attempts):
            try:
                if self._HTTPClient__session.closed:
                    await self.login(cast(str, self.token))

                processed_data = self._process_payload(payload, files)
                if isinstance(processed_data, FormData):
                    kwargs["data"] = processed_data
                else:
                    kwargs["json"] = processed_data
                await self.global_lock.wait()

                if self.proxy:
                    kwargs["proxy"] = self.proxy[0]
                    kwargs["proxy_auth"] = self.proxy[1]

                async with self._HTTPClient__session.request(route.method, route.url, **kwargs) as response:
                    result = await response_decode(response)

                    if response.status == 429:
                        result = cast(dict[str, str], result)
                        if result.get("global", False):
                            self.log_ratelimit(
                                self.logger.warning,
                                f"Bot has exceeded global ratelimit,"
                                f" locking REST API for {result['retry_after']} seconds",
                            )
                            self.global_lock.set_reset_time(float(result["retry_after"]))
                        elif result.get("message") == "The resource is being rate limited.":
                            raise Ratelimited(
                                f"{route.resolved_endpoint} The resource is being rate limited!"
                                f" Reset in {result.get('retry_after')} seconds",
                                result.get("retry_after"),
                            )
                        else:
                            raise Ratelimited(f"{route.resolved_endpoint} Has exceeded its ratelimit!")
                    elif response.status in {500, 502, 504}:
                        self.logger.warning(
                            f"{route.resolved_endpoint} Received {response.status}..."
                            f" retrying in {1 + attempt * 2} seconds"
                        )
                        await asyncio.sleep(1 + attempt * 2)
                        continue

                    if not 300 > response.status >= 200:
                        await self._raise_exception(response, route, result)
                    return result
            except OSError as e:
                if attempt < self._max_attempts - 1 and e.errno in (54, 10054):
                    await asyncio.sleep(1 + attempt * 2)
                    continue
                raise
