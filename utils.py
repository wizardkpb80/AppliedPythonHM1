import time
import asyncio

def run_async(func, *args):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(func(*args))

def time_decorator(func):
    """
    A decorator to measure the execution time of a function.
    """

    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)  # Calls the function asynchronously if it's async
        end_time = time.time()
        print(f"Фунцкия {func.__name__}' выполнение {end_time - start_time:.2f} секундах")
        return result

    return wrapper


# Synchronous version (for non-async functions)
def time_decorator_sync(func):
    """
    A decorator to measure the execution time of a function (for sync functions).
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)  # Calls the function synchronously
        end_time = time.time()
        print(f"Фунцкия '{func.__name__}' выполнение {end_time - start_time:.2f} секундах")
        return result

    return wrapper
