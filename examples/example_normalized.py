import asyncio
import time

async def blocking_task():
    print('Task starting')
    time.sleep(2)
    print('Task done')

async def main():
    print('Main running the blocking task')
    coro = blocking_task()
    print('Main doing other things')
    await asyncio.sleep(0)
    await coro
asyncio.run(main())