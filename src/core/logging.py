"""
Provide logging functionality for the bot.
"""

import inspect
import logging
import sys
from datetime import timedelta
from typing import Optional

from loguru._logger import Core
from loguru._logger import Logger as _Logger
from loguru._logger import _defaults

__all__ = ("Logger", "InterceptHandler")


class Logger(_Logger):
    """
    The Loguru library provides loggers to deal with logging in Python.
    This class provides a pre-instanced (and configured) logger for the bot.
    * Stop using print() and use this instead smh.
    """

    def __init__(
        self,
        log_format: Optional[str] = _defaults.LOGURU_FORMAT,
        level: Optional[str] = "WARNING",
        retention: Optional[int] = 0,
    ) -> None:
        """
        Initialize the logger instance.

        :param log_format: The format of the logs.
        :type log_format: Optional[str]
        :param level: The logging level.
        :type level: Optional[str]
        :param retention: The retention time for the logs in days.
        :type retention: Optional[int]
        """
        super().__init__(
            core=Core(),
            exception=None,
            depth=0,
            record=False,
            lazy=False,
            colors=False,
            raw=False,
            capture=True,
            patchers=[],
            extra={},
        )
        self.add(sys.stderr, level=level, diagnose=False, enqueue=True, format=log_format)
        if retention < 0:
            self.warning("Retention time cannot be negative. Disabling log saving.")
        elif retention > 0:
            self.add(
                "./logs/{time:YYYY-MM-DD_HH-mm-ss_SSS}.log",
                rotation="00:00",
                retention=timedelta(days=retention),
                encoding="utf-8",
                compression="gz",
                diagnose=False,
                level=level,
                enqueue=True,
                format=log_format,
            )
        self.debug(f"Logger initialized with level {level}.")

    def log(self, level, message, *args, **kwargs):
        if isinstance(level, int):
            level = logging.getLevelName(level)
        return super().log(level, message, *args, **kwargs)

    def critical_exc(self, message, *args, **kwargs):
        r"""Convenience method for logging a ``'CRITICAL'`` error with exception information."""
        options = (True,) + self._options[1:]
        self._log("CRITICAL", False, options, message, args, kwargs)


class InterceptHandler(logging.Handler):
    """
    This class is used to intercept standard logging messages and redirect them to Loguru.
    """

    def __init__(self, logger: Logger) -> None:
        super().__init__()
        self.logger = logger

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = self.logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        self.logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
