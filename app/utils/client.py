from hhaven.client import Client
from hhaven.exceptions import HHavenException
import logging

client = Client()

async def get_client():
    try:
        if not client._built:
            await client.build()
        return client
    except HHavenException as e:
        logging.error(f"Client error: {e}")
        raise
