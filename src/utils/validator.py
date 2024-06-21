import binascii
from base64 import urlsafe_b64decode
from typing import List, Optional

from .const import TOKEN_REGEX, URL_REGEX

__all__ = ("Validator",)


class Validator:
    """
    This class contains methods to validate or check different stuff.
    """

    @classmethod
    def find_urls(cls, text: str) -> Optional[List[str]]:
        """
        Find all URLs in a string.

        :param text: The text to search.
        :type text: str

        :return: The found URLs.
        :rtype: Optional[List[str]]
        """
        return URL_REGEX.findall(text)

    @classmethod
    def find_tokens(cls, text: str) -> Optional[List[str]]:
        """
        Find all tokens in a string.

        :param text: The text to search.
        :type text: str

        :return: The found tokens.
        :rtype: Optional[List[str]]
        """
        return TOKEN_REGEX.findall(text)

    @staticmethod
    async def is_valid_token(token: str) -> bool:
        """
        Check if a token is valid.

        :param token: The token to check.
        :type token: str

        :return: If the token is valid.
        :rtype: bool
        """
        try:
            uid = urlsafe_b64decode(token.split(".")[0] + "==")
        except binascii.Error:
            return False
        else:
            return uid.isdigit()
