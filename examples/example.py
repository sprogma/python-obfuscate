import asyncio
import time

# блокирующая задача, зависящая от подсистемы ввода/вывода
async def blocking_task():
    # вывод сообщения
    print('Task starting')
    # блокировка на некоторое время
    time.sleep(2)
    # вывод сообщения
    print('Task done')

# главная корутина
async def main():
    # вывод сообщения
    print('Main running the blocking task')
    # создание корутины для блокирующей задачи
    coro = blocking_task()
    # планирование задачи
    # вывод сообщения
    print('Main doing other things')
    # позволяем запланированной задаче запуститься
    await asyncio.sleep(0)
    # ожидание завершения задачи
    await coro

# запуск asyncio-программы
asyncio.run(main())