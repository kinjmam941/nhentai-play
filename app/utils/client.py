from hhaven.client import Client
from hhaven.exceptions import HHavenException
import logging

# Initialize the client instance
client = Client()

async def initialize_client():
    """Initialize the client on startup"""
    try:
        if not client._built:
            await client.build()
        return client
    except HHavenException as e:
        logging.error(f"Client initialization failed: {e}")
        raise
