#!/usr/bin/env python3
"""
Wrapper script to run the webhook client properly as a module.

This ensures package imports work correctly.
"""

if __name__ == "__main__":
    from client import client
    # The client module will run when imported due to its if __name__ == "__main__" block
    # We need to trigger it differently
    import sys
    import asyncio

    # Import and run the client's main function
    from client.client import main
    asyncio.run(main())
