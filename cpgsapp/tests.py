import asyncio
import threading
import time


def capture():

        while True:
            time.sleep(2)
            print("Capturing")


Thread = threading.Thread(target=capture)
Thread.start()

while True:

    time.sleep(2)
    print('hello')