import asyncio

import decouple

from src.main import Client


async def main() -> None:
    """
    Start the application.
    """
    await Client().astart(decouple.config("token"))


if __name__ == "__main__":
    asyncio.run(main())
