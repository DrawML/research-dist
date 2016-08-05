import asyncio

@asyncio.coroutine
def test(number):
    yield from asyncio.sleep(number)
    print("complete -", number)


@asyncio.coroutine
def new_task():
    for i in range(5):
        print("hello -", i)
        yield from asyncio.sleep(1)
    print("finish of new task.")

@asyncio.coroutine
def haaam(number):
    yield from asyncio.sleep(number)
    print("add new task.")
    ntask = asyncio.ensure_future(new_task())

loop = asyncio.get_event_loop()
tasks = [
    asyncio.ensure_future(haaam(3)),
    asyncio.ensure_future(test(2)),
    asyncio.ensure_future(test(3)),
    asyncio.ensure_future(test(4))]
#loop.run_forever()
loop.run_until_complete(asyncio.wait(tasks))
loop.close()