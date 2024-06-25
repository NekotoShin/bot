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

import interactions


def return_option() -> interactions.StringSelectOption:
    """
    Generate a return option for the settings command.

    :return: The return option.
    :rtype: interactions.StringSelectOption
    """
    return interactions.StringSelectOption(
        label="返回",
        value="return",
        description="回到上一個選單",
        emoji="🔙",
    )
