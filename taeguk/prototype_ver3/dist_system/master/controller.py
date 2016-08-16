import asyncio
from .slave import SlaveManager
from .task import TaskManager


async def run_heartbeat():
    # send "Heart Beat Req" using protocol.

    asyncio.sleep(SlaveManager.HEARTBEAT_INTERVAL)
    expired_slaves, leak_tasks = SlaveManager().purge()
    TaskManager().redo_leak_task(leak_tasks)
